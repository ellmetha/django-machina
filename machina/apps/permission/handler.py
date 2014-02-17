# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from guardian.core import ObjectPermissionChecker

# Local application / specific library imports

Post = get_model('conversation', 'Post')


class PermissionHandler(object):

    # Filtering methods
    # --

    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that can be seen or read
        by the specified user (at least).
        """
        checker = ObjectPermissionChecker(user)

        # Any superuser should see all the forums
        if user.is_superuser:
            return qs

        # Check whether the forums can be viewed by the given user
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
        posts = Post.objects.filter(topic__forum__in=forums).order_by('-created')

        if not posts.exists():
            return None
        return posts[0]

    # Verification methods
    # --

    def can_edit_post(self, post, user):
        """
        Given a forum post, checks whether the user can edit the latter.
        """
        checker = ObjectPermissionChecker(user)

        # A user can edit a post if...
        #     he is a superuser
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
        #     he is a superuser
        #     he is the original poster of the forum post
        #     he belongs to the forum moderators
        can_edit = (user.is_superuser
                    or (post.poster == user and checker.has_perm('can_delete_own_posts', post.topic.forum))
                    or checker.has_perm('can_delete_posts', post.topic.forum))
        return can_edit

    # Common
    # --

    def _get_hidden_forum_ids(self, forums, checker):
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
                    # If one forum can not be seen by a given user, all of its descendant
                    # should also be hidden.
                    forum_and_descendants = forum.get_descendants(include_self=True)
                    hidden_forums.extend(forum_and_descendants.values_list('id', flat=True))
        return hidden_forums
