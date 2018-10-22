"""
    Forum tracking managers
    =======================

    This module defines managers provided by the ``forum_tracking`` application.

"""

from django.db import models

from machina.core.loading import get_class


ForumVisibilityContentTree = get_class('forum.visibility', 'ForumVisibilityContentTree')


class ForumReadTrackManager(models.Manager):
    """ Provides useful manager methods for the ``ForumReadTrack`` model. """

    def get_unread_forums_from_list(self, forums, user):
        """ Filter a list of forums and return only those which are unread.

        Given a list of forums find and returns the list of forums that are unread for the passed
        user. If a forum is unread all of its ancestors are also unread and will be included in the
        final list.
        """
        unread_forums = []
        visibility_contents = ForumVisibilityContentTree.from_forums(forums)
        forum_ids_to_visibility_nodes = visibility_contents.as_dict

        tracks = super().get_queryset().select_related('forum').filter(
            user=user,
            forum__in=forums)
        tracked_forums = []

        for track in tracks:
            forum_last_post_on = forum_ids_to_visibility_nodes[track.forum_id].last_post_on
            if (forum_last_post_on and track.mark_time < forum_last_post_on) \
                    and track.forum not in unread_forums:
                unread_forums.extend(track.forum.get_ancestors(include_self=True))
            tracked_forums.append(track.forum)

        for forum in forums:
            if forum not in tracked_forums and forum not in unread_forums \
                    and forum.direct_topics_count > 0:
                unread_forums.extend(forum.get_ancestors(include_self=True))

        return list(set(unread_forums))
