# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db import models

# Local application / specific library imports


class ForumReadTrackManager(models.Manager):
    def get_unread_forums_from_list(self, forums, user):
        """
        Given a list of forums find and returns the list of forums that are unread
        for the passed user.
        If a forum is unread all of its ancestors are also unread and will be
        included in the final list.
        """
        super_self = super(ForumReadTrackManager, self)
        get_queryset = (super_self.get_query_set
                        if hasattr(super_self, 'get_query_set')
                        else super_self.get_queryset)

        unread_forums = []

        tracks = get_queryset().select_related('forum').filter(
            user=user,
            forum__in=forums)
        tracked_forums = []

        for track in tracks:
            if (track.forum.last_post_on and track.mark_time < track.forum.last_post_on) \
                    and track.forum not in unread_forums:
                unread_forums.extend(track.forum.get_ancestors(include_self=True))
            tracked_forums.append(track.forum)

        for forum in forums:
            if forum not in tracked_forums and forum not in unread_forums and forum.topics.count() > 0:
                unread_forums.extend(forum.get_ancestors(include_self=True))

        return list(set(unread_forums))
