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
        """
        unread_forums = []

        tracks = super(ForumReadTrackManager, self).get_query_set().filter(
            user=user,
            forum__in=forums)
        tracked_forums = []

        for track in tracks:
            if track.mark_time < track.forum.updated:
                unread_forums.extend(track.forum.get_ancestors(include_self=True))
            tracked_forums.append(track.forum)

        for forum in forums:
            if forum not in tracked_forums and forum not in unread_forums and forum.topics.count() > 0:
                unread_forums.extend(forum.get_ancestors(include_self=True))

        return list(set(unread_forums))
