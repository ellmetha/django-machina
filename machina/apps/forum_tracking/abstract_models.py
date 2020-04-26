"""
    Forum tracking abstract models
    ==============================

    This module defines abstract models provided by the ``forum_tracking`` application.

"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from machina.core.loading import get_class


ForumReadTrackManager = get_class('forum_tracking.managers', 'ForumReadTrackManager')


class AbstractForumReadTrack(models.Model):
    """ Represents a track which records which forums have been read by a given user. """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='forum_tracks', on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    forum = models.ForeignKey(
        'forum.Forum', related_name='tracks', on_delete=models.CASCADE, verbose_name=_('Forum'),
    )
    mark_time = models.DateTimeField(auto_now=True, db_index=True)

    objects = ForumReadTrackManager()

    class Meta:
        abstract = True
        app_label = 'forum_tracking'
        unique_together = ['user', 'forum', ]
        verbose_name = _('Forum track')
        verbose_name_plural = _('Forum tracks')

    def __str__(self):
        return '{} - {}'.format(self.user, self.forum)


class AbstractTopicReadTrack(models.Model):
    """ Represents a track which records which topics have been read by a given user. """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='topic_tracks', on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    topic = models.ForeignKey(
        'forum_conversation.Topic', related_name='tracks', on_delete=models.CASCADE,
        verbose_name=_('Topic'),
    )
    mark_time = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
        app_label = 'forum_tracking'
        unique_together = ['user', 'topic', ]
        verbose_name = _('Topic track')
        verbose_name_plural = _('Topic tracks')

    def __str__(self):
        return '{} - {}'.format(self.user, self.topic)
