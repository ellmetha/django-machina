# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime as dt
from functools import reduce

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import _get_queryset
from django.utils.timezone import now
from mptt.utils import get_cached_trees

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
Post = get_model('forum_conversation', 'Post')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')

ForumPermissionChecker = get_class('forum_permission.checker', 'ForumPermissionChecker')

get_anonymous_user_forum_key = get_class(
    'forum_permission.shortcuts', 'get_anonymous_user_forum_key')


class PermissionHandler(object):
    """
    The PermissionHandler allows to filter lists of forums and to perform
    permission verifications on forums. It uses the ForumPermissionChecker
    class to perform these verifications.
    """
    def __init__(self):
        # This dictionary will store the forums that are granted for a specific
        # lit of permission codenames and a given user.
        self._granted_forums_cache = {}

        # This one will store the ancestors of the forums that will be used to
        # perform permission checks.
        self._forum_ancestors_cache = {}

        # This one will store ForumPermissionChecker instances for users whose
        # permissions will be checked.
        self._user_perm_checkers_cache = {}

    # Filtering methods
    # --

    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that can be seen or read
        by the specified user (at least).
        """
        # Any superuser should see all the forums
        if user.is_superuser:
            return qs

        # Check whether the forums can be viewed by the given user
        forums_to_hide = self._get_hidden_forum_ids(qs, user)

        return qs.exclude(id__in=forums_to_hide)

    def get_forum_last_post(self, forum, user):
        """
        Given a forum, fetch the last post that can be read by the passed user.
        """
        forums = forum.get_descendants(include_self=True)
        hidden_forums = []

        # Only non-superusers permissions are checked against the considered forums
        if not user.is_superuser:
            hidden_forums = self._get_hidden_forum_ids(forums, user)

        forums = forums.exclude(id__in=hidden_forums)
        return Post.approved_objects.filter(topic__forum__in=forums).order_by('-created').first()

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
        can_add_post = self._perform_basic_permission_check(
            topic.forum, user, 'can_reply_to_topics') and (
                not topic.is_locked or
                self._perform_basic_permission_check(
                    topic.forum, user, 'can_reply_to_locked_topics'))
        return can_add_post

    def can_edit_post(self, post, user):
        """
        Given a forum post, checks whether the user can edit the latter.
        """
        checker = self._get_checker(user)

        # A user can edit a post if...
        #     he is a superuser
        #     he is the original poster of the forum post
        #     he belongs to the forum moderators
        is_author = self._is_post_author(post, user)
        can_edit = (user.is_superuser or
                    (
                        is_author and checker.has_perm('can_edit_own_posts', post.topic.forum) and
                        not post.topic.is_locked
                    ) or
                    checker.has_perm('can_edit_posts', post.topic.forum))
        return can_edit

    def can_delete_post(self, post, user):
        """
        Given a forum post, checks whether the user can delete the latter.
        """
        checker = self._get_checker(user)

        # A user can delete a post if...
        #     he is a superuser
        #     he is the original poster of the forum post
        #     he belongs to the forum moderators
        is_author = self._is_post_author(post, user)
        can_delete = (user.is_superuser or
                      (is_author and checker.has_perm('can_delete_own_posts', post.topic.forum)) or
                      checker.has_perm('can_delete_posts', post.topic.forum))
        return can_delete

    # Polls

    def can_create_polls(self, forum, user):
        """
        Given a forum, checks whether the user can add a topic with an embedded poll.
        """
        return self._perform_basic_permission_check(forum, user, 'can_create_polls')

    def can_vote_in_poll(self, poll, user):
        """
        Given a poll, checks whether the user can answer to it.
        """
        # First we have to check if the poll is curently open
        if poll.duration:
            poll_dtend = poll.created + dt.timedelta(days=poll.duration)
            if poll_dtend < now():
                return False

        # Is this user allowed to vote in polls in the current forum ?
        can_vote = self._perform_basic_permission_check(
            poll.topic.forum, user, 'can_vote_in_polls') and not poll.topic.is_locked

        # Retrieve the user votes for the considered poll
        user_votes = TopicPollVote.objects.filter(
            poll_option__poll=poll)
        if user.is_anonymous():
            forum_key = get_anonymous_user_forum_key(user)
            if forum_key:
                user_votes = user_votes.filter(anonymous_key=forum_key)
            else:
                # If the forum key of the anonymous user cannot be retrieved, the user
                # should not be allowed to vote in the considered poll.
                user_votes = user_votes.none()
                can_vote = False
        else:
            user_votes = user_votes.filter(voter=user)

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

    # Topic subscription

    def can_subscribe_to_topic(self, topic, user):
        """
        Given a topic, checks whether the user can add it to his subscription list.
        """
        # A user can subscribe to topics if he is authenticated and if he has the permission to read
        # the related forum. Of course a user can subscribe only if he has not already subscribed to
        # the considered topic.
        return user.is_authenticated() and not topic.has_subscriber(user) \
            and self._perform_basic_permission_check(topic.forum, user, 'can_read_forum')

    def can_unsubscribe_from_topic(self, topic, user):
        """
        Given a topic, checks whether the user can remove it from his subscription list.
        """
        # A user can unsubscribe from topics if he is authenticated and if he has the permission to
        # read the related forum. Of course a user can unsubscribe only if he is already a
        # a subscriber of the considered topic.
        return user.is_authenticated() and topic.has_subscriber(user) \
            and self._perform_basic_permission_check(topic.forum, user, 'can_read_forum')

    # Moderation

    def get_moderation_queue_forums(self, user):
        """
        Returns the list of forums whose posts can be approved by the considered
        user.
        """
        return self._get_forums_for_user(user, ['can_approve_posts', ])

    def can_access_moderation_queue(self, user):
        """
        Returns True if the passed user can access the moderation queue.  The latest
        allows the moderator to approve posts.
        """
        moderated_forums = self.get_moderation_queue_forums(user)
        return moderated_forums.exists()

    def can_lock_topics(self, forum, user):
        """
        Given a forum, checks whether the user can lock its topics.
        """
        return self._perform_basic_permission_check(forum, user, 'can_lock_topics')

    def can_move_topics(self, forum, user):
        """
        Given a forum, checks whether the user can move its topics to another forum.
        """
        return self._perform_basic_permission_check(forum, user, 'can_move_topics')

    def get_target_forums_for_moved_topics(self, user):
        """
        Returns a list of forums in which the considered user can add topics
        that have been moved from another forum.
        """
        return self._get_forums_for_user(user, ['can_move_topics', ]) \
            .filter(type=Forum.FORUM_POST)

    def can_delete_topics(self, forum, user):
        """
        Given a forum, checks whether the user can delete its topics.
        Note: the ``can_delete_posts`` permission is used here because
        a user who can delete all the posts of a topic is also able to
        delete the topic itself.
        """
        return self._perform_basic_permission_check(forum, user, 'can_delete_posts')

    def can_update_topics_to_normal_topics(self, forum, user):
        """
        Given a forum, checks whether the user can change its topic types to normal
        topics.
        """
        return self._perform_basic_permission_check(forum, user, 'can_edit_posts')

    def can_update_topics_to_sticky_topics(self, forum, user):
        """
        Given a forum, checks whether the user can change its topic types to sticky
        topics.
        """
        return self._perform_basic_permission_check(forum, user, 'can_edit_posts') \
            and self._perform_basic_permission_check(forum, user, 'can_post_stickies')

    def can_update_topics_to_announces(self, forum, user):
        """
        Given a forum, checks whether the user can change its topic types to announces.
        """
        return self._perform_basic_permission_check(forum, user, 'can_edit_posts') \
            and self._perform_basic_permission_check(forum, user, 'can_post_announcements')

    def can_approve_posts(self, forum, user):
        """
        Given a forum, checks whether the user can approve its posts.
        """
        return self._perform_basic_permission_check(forum, user, 'can_approve_posts')

    # Common
    # --

    def _is_post_author(self, post, user):
        return (post.poster == user) if user.is_authenticated() \
            else (post.anonymous_key is not None and
                  post.anonymous_key == get_anonymous_user_forum_key(user))

    def _get_hidden_forum_ids(self, forums, user):
        """
        Given a set of forums and a user, returns the list of forums that are not visible
        by this user.
        """
        visible_forums = self._get_forums_for_user(
            user, ['can_see_forum', 'can_read_forum', ], use_tree_hierarchy=True)
        return forums.exclude(id__in=[f.id for f in visible_forums])

    def _get_forums_for_user(self, user, perm_codenames, use_tree_hierarchy=False):
        """
        Returns all the forums that satisfy the given list of permission
        codenames. User and group forum permissions are used.

        If the ``use_tree_hierarchy`` keyword argument is set the granted forums will be filtered
        so that a forum which has an ancestor which is not in the granted forums set will not be
        returned.
        """
        granted_forums_cache_key = '{}__{}'.format(
            ':'.join(perm_codenames),
            user.id if not user.is_anonymous() else 'anonymous')

        if granted_forums_cache_key in self._granted_forums_cache:
            return self._granted_forums_cache[granted_forums_cache_key]

        forum_queryset = _get_queryset(Forum)

        # First check if the user is a superuser and if so, returns the forum
        # queryset immediately.
        if user.is_superuser:  # pragma: no cover
            forum_objects = forum_queryset

        else:
            # Generates the appropriate queryset filter in order to handle both
            # authenticated users and anonymous users.
            user_kwargs_filter = {'anonymous_user': True} if user.is_anonymous() \
                else {'user': user}

            # Get all the user permissions for the considered user.
            user_perms = UserForumPermission.objects \
                .filter(**user_kwargs_filter) \
                .filter(permission__codename__in=perm_codenames)

            globally_granted_user_perms = list(
                filter(lambda p: p.has_perm and p.forum is None, user_perms))
            per_forum_granted_user_perms = list(
                filter(lambda p: p.has_perm and p.forum is not None, user_perms))
            per_forum_nongranted_user_perms = list(
                filter(lambda p: not p.has_perm and p.forum is not None, user_perms))

            user_granted_forum_ids = [p.forum_id for p in per_forum_granted_user_perms]
            user_nongranted_forum_ids = [p.forum_id for p in per_forum_nongranted_user_perms]

            if not user.is_anonymous():
                user_model = get_user_model()
                # Get all the group permissions for the considered user.
                group_perms = GroupForumPermission.objects \
                    .filter(**{
                        'group__{0}'.format(user_model.groups.field.related_query_name()): user}) \
                    .filter(permission__codename__in=perm_codenames)

                globally_granted_group_perms = list(
                    filter(lambda p: p.has_perm and p.forum is None, group_perms))
                per_forum_granted_group_perms = list(
                    filter(lambda p: p.has_perm and p.forum is not None, group_perms))
                per_forum_nongranted_group_perms = list(
                    filter(lambda p: not p.has_perm and p.forum is not None, group_perms))

                group_granted_forum_ids = [p.forum_id for p in per_forum_granted_group_perms]
                group_nongranted_forum_ids = [p.forum_id for p in per_forum_nongranted_group_perms]

                if globally_granted_user_perms or globally_granted_group_perms:
                    forum_objects = forum_queryset.filter(
                        ~Q(pk__in=(user_nongranted_forum_ids + group_nongranted_forum_ids)))
                else:
                    forum_objects = forum_queryset.filter(
                        Q(pk__in=user_granted_forum_ids) | Q(pk__in=group_granted_forum_ids)) \
                        .filter(~Q(pk__in=(user_nongranted_forum_ids + group_nongranted_forum_ids)))
            else:
                if globally_granted_user_perms:
                    forum_objects = forum_queryset.filter(~Q(pk__in=user_nongranted_forum_ids))
                else:
                    forum_objects = forum_queryset.filter(Q(pk__in=user_granted_forum_ids)) \
                        .filter(~Q(pk__in=user_nongranted_forum_ids))

            if not user.is_anonymous() and not forum_objects.exists() \
                    and set(perm_codenames).issubset(set(
                        machina_settings.DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS)):
                forum_objects = forum_queryset

            if use_tree_hierarchy:
                forum_objects = self._filter_granted_forums_using_tree(forum_objects)

        self._granted_forums_cache[granted_forums_cache_key] = forum_objects
        return forum_objects

    def _filter_granted_forums_using_tree(self, granted_forums):
        top_nodes = self._get_top_nodes()
        d = reduce(
            lambda a, b: a + self._filter_granted_node_using_tree(b, granted_forums), top_nodes, [])
        return Forum.objects.filter(id__in=d)

    def _filter_granted_node_using_tree(self, f, granted_forums):
        if f in granted_forums:
            return [f.id, ] + reduce(
                lambda a, b: a + self._filter_granted_node_using_tree(b, granted_forums),
                f.get_children(), [])
        return []

    def _get_top_nodes(self):
        if not hasattr(self, '_top_nodes'):
            self._top_nodes = get_cached_trees(Forum.objects.all())
        return self._top_nodes

    def _perform_basic_permission_check(self, forum, user, permission):
        """
        Given a forum and a user, checks whether the latter has the passed
        permission.
        The workflow is:

            1. The permission is granted if the user is a superuser
            2. If not, a check is performed with the given permission
        """
        checker = self._get_checker(user)

        # The action is granted if...
        #     the user is the superuser
        #     the user has the permission to do so
        check = (user.is_superuser or checker.has_perm(permission, forum))
        return check

    def _get_checker(self, user):
        """
        Return a ForumPermissionChecker instance for the given user.
        """
        user_perm_checkers_cache_key = user.id if not user.is_anonymous() else 'anonymous'

        if user_perm_checkers_cache_key in self._user_perm_checkers_cache:
            return self._user_perm_checkers_cache[user_perm_checkers_cache_key]

        checker = ForumPermissionChecker(user)
        self._user_perm_checkers_cache[user_perm_checkers_cache_key] = checker
        return checker
