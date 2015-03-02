# -*- coding: utf-8 -*-

# Standard library imports
from datetime import timedelta

# Third party imports
from django.utils.timezone import now
from guardian.core import ObjectPermissionChecker

# Local application / specific library imports
from machina.core.db.models import get_model

Post = get_model('forum_conversation', 'Post')


class PermissionHandler(object):

    # Filtering methods
    # --

    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that can be seen or read
        by the specified user (at least).
        """
        checker = ObjectPermissionChecker(user)

        # Any superuser should see all the forums
        if user.is_superuser:
            return qs

        # Check whether the forums can be viewed by the given user
        forums_to_hide = self._get_hidden_forum_ids(qs, checker)

        return qs.exclude(id__in=forums_to_hide)

    def get_forum_last_post(self, forum, user):
        """
        Given a forum, fetch the last post that can be read by the passed user.
        """
        checker = ObjectPermissionChecker(user)

        forums = forum.get_descendants(include_self=True)
        hidden_forums = []

        # Only non-superusers permissions are checked against the considered forums
        if not user.is_superuser:
            hidden_forums = self._get_hidden_forum_ids(forums, checker)

        forums = forums.exclude(id__in=hidden_forums)
        posts = Post.approved_objects.filter(topic__forum__in=forums).order_by('-created')

        if not posts.exists():
            return None
        return posts[0]

    # Verification methods
    # --

    # Forums

    def can_read_forum(self, forum, user):
        """
        Given a forum, checks whether the user can read its content.
        """
        return self._perform_basic_permission_check(forum, user, 'can_read_forum')

    # Posts and topics

    def can_add_topic(self, forum, user):
        """
        Given a forum, checks whether the user can append topics to it.
        """
        return self._perform_basic_permission_check(forum, user, 'can_start_new_topics')

    def can_add_stickies(self, forum, user):
        """
        Given a forum, checks whether the user can append stickies to it.
        """
        return self._perform_basic_permission_check(forum, user, 'can_post_stickies')

    def can_add_announcements(self, forum, user):
        """
        Given a forum, checks whether the user can append announcements to it.
        """
        return self._perform_basic_permission_check(forum, user, 'can_post_announcements')

    def can_post_without_approval(self, forum, user):
        """
        Given a forum, checks whether the user can add a posts and topics without approval.
        """
        return self._perform_basic_permission_check(forum, user, 'can_post_without_approval')

    def can_add_post(self, topic, user):
        """
        Given a topic, checks whether the user can append posts to it.
        """
        return self._perform_basic_permission_check(topic.forum, user, 'can_reply_to_topics')

    def can_edit_post(self, post, user):
        """
        Given a forum post, checks whether the user can edit the latter.
        """
        checker = ObjectPermissionChecker(user)

        # A user can edit a post if...
        #     he is a superuser
        #     he is the original poster of the forum post
        #     he belongs to the forum moderators
        can_edit = (user.is_superuser
                    or (post.poster == user and checker.has_perm('can_edit_own_posts', post.topic.forum))
                    or checker.has_perm('can_edit_posts', post.topic.forum))
        return can_edit

    def can_delete_post(self, post, user):
        """
        Given a forum post, checks whether the user can delete the latter.
        """
        checker = ObjectPermissionChecker(user)

        # A user can delete a post if...
        #     he is a superuser
        #     he is the original poster of the forum post
        #     he belongs to the forum moderators
        can_delete = (user.is_superuser
                      or (post.poster == user and checker.has_perm('can_delete_own_posts', post.topic.forum))
                      or checker.has_perm('can_delete_posts', post.topic.forum))
        return can_delete

    # Polls

    def can_create_polls(self, forum, user):
        """
        Given a forum, checks whether the user can add a topic with an embedded poll.
        """
        return self._perform_basic_permission_check(forum, user, 'can_create_poll')

    def can_vote_in_poll(self, poll, user):
        """
        Given a poll, checks whether the user can answer to it.
        """
        # First we have to check if the poll is curently open
        if poll.duration:
            poll_dtend = poll.created + timedelta(days=poll.duration)
            if poll_dtend < now():
                return False

        # Is this user allowed to vote in polls in the current forum ?
        can_vote = self._perform_basic_permission_check(poll.topic.forum, user, 'can_vote_in_polls')

        # Retrieve the user votes for the considered poll
        user_votes = user.poll_votes.filter(poll_option__poll=poll)

        # If the user has already voted, he can vote again if the vote changes are allowed
        if user_votes.exists() and can_vote:
            can_vote = poll.user_changes

        return can_vote

    # Attachments

    def can_attach_files(self, forum, user):
        """
        Given a forum, checks whether the user can add attachments to posts.
        """
        return self._perform_basic_permission_check(forum, user, 'can_attach_file')

    def can_download_files(self, forum, user):
        """
        Given a forum, checks whether the user can download files attached to posts.
        """
        return self._perform_basic_permission_check(forum, user, 'can_download_file')

    # Common
    # --

    def _get_hidden_forum_ids(self, forums, checker):
        """
        Given a set of forums and an initialized checker, returns the list of forums
        that are not visible by the user or the group associated with this checker.
        """
        hidden_forums = []
        for forum in forums:
            if forum.id not in hidden_forums:
                # First cheks if any of the forum ancestors is hidden
                ancestors_visible = True
                for ancestor in forum.get_ancestors():
                    if not checker.has_perm('can_see_forum', ancestor) and not checker.has_perm('can_read_forum', ancestor):
                        ancestors_visible = False
                        break

                if (ancestors_visible is False) or (not checker.has_perm('can_see_forum', forum) and
                                                    not checker.has_perm('can_read_forum', forum)):
                    # If one forum can not be seen by a given user, all of its descendant
                    # should also be hidden.
                    forum_and_descendants = forum.get_descendants(include_self=True)
                    hidden_forums.extend(forum_and_descendants.values_list('id', flat=True))
        return hidden_forums

    def _perform_basic_permission_check(self, forum, user, permission):
        """
        Given a forum and a user, checks whether the latter has the passed
        permission.
        The workflow is:

            1. The permission is granted if the user is a superuser
            2. If not, a check is performed with the given permission
        """
        checker = ObjectPermissionChecker(user)

        # The action is granted if...
        #     the user is the superuser
        #     the user has the permission to do so
        check = (user.is_superuser
                 or checker.has_perm(permission, forum))
        return check
