# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class ForumReadTrackManager(models.Manager):
    def get_unread_forums_from_list(self, forums, user):
        """
        Given a list of forums find and returns the list of forums that are unread
        for the passed user.
        If a forum is unread all of its ancestors are also unread and will be
        included in the final list.
        """
        unread_forums = []

        tracks = super(ForumReadTrackManager, self).get_queryset().select_related('forum').filter(
            user=user,
            forum__in=forums)
        tracked_forums = []

        for track in tracks:
            if (track.forum.last_post_on and track.mark_time < track.forum.last_post_on) \
                    and track.forum not in unread_forums:
                unread_forums.extend(track.forum.get_ancestors(include_self=True))
            tracked_forums.append(track.forum)

        for forum in forums:
            if forum not in tracked_forums and forum not in unread_forums \
                    and forum.topics.filter(approved=True).count() > 0:
                unread_forums.extend(forum.get_ancestors(include_self=True))

        return list(set(unread_forums))
