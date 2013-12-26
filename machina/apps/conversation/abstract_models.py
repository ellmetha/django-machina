# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.compat import AUTH_USER_MODEL
from machina.models.abstract_models import DatedModel
from machina.models.fields import MarkupTextField


TOPIC_TYPES = Choices(
    (0, 'topic_post', _('Default topic')),
    (1, 'topic_global', _('Global topic')),
    (2, 'topic_announce', _('Announce')),
    (3, 'topic_sticky', _('Sticky')),
)

TOPIC_STATUSES = Choices(
    (0, 'topic_unlocked', _('Topic unlocked')),
    (1, 'topic_locked', _('Topic locked')),
    (2, 'topic_moved', _('Topic moved')),
)


class AbstractTopic(DatedModel):
    """
    Represents a forum topic.
    """
    forum = models.ForeignKey('forum.Forum', verbose_name=_('Topic forum'), related_name='topics')
    poster = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('Poster'))
    subject = models.CharField(verbose_name=_('Subject'), max_length=255)

    # Sticky, Announce, Global topic or Default topic ; that's what a topic can be
    type = models.PositiveSmallIntegerField(choices=TOPIC_TYPES, verbose_name=_('Topic type'), db_index=True)

    # A topic can be locked, unlocked or moved
    status = models.PositiveIntegerField(choices=TOPIC_STATUSES, verbose_name=_('Topic status'), db_index=True)

    # The number of posts included in this topic
    posts_count = models.PositiveIntegerField(verbose_name=_('Posts count'), blank=True, default=0)

    # The number of time the topic has been viewed
    views_count = models.PositiveIntegerField(verbose_name=_('Views count'), blank=True, default=0)

    # Many users can subscribe to this topic
    subscribers = models.ManyToManyField(AUTH_USER_MODEL, related_name='subscriptions', verbose_name=_('Subscribers'), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-updated', ]
        get_latest_by = 'updated'
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        app_label = 'conversation'

    def __unicode__(self):
        return '{}'.format(self.subject)

    @property
    def first_post(self):
        """
        Try to fetch the first post associated with the current topic and caches it to
        lighten the next request.
        """
        if not hasattr(self, '_first_post'):
            posts = self.posts.all().order_by('created')
            self._first_post = posts[0] if posts.exists() else None
        return self._first_post

    @property
    def last_post(self):
        """
        Try to fetch the last post associated with the current topic and caches it to
        lighten the next request.
        """
        if not getattr(self, '_last_post', None):
            posts = self.posts.all().order_by('-created')
            self._last_post = posts[0] if posts.exists() else None
        return self._last_post


class AbstractPost(DatedModel):
    """
    Represents a forum post. A forum post is always linked to a topic.
    """
    topic = models.ForeignKey('conversation.Topic', verbose_name=_('Topic'), related_name='posts')
    poster = models.ForeignKey(AUTH_USER_MODEL, related_name='posts', verbose_name=_('Poster'))

    # Content
    content = MarkupTextField(verbose_name=_('Content'))

    # A topic can be edited for several reason (eg. moderation) ; the reason why it has been updated can be specified
    update_reason = models.CharField(max_length=255, verbose_name=_('Update reason'), blank=True, null=True)

    # Tracking data
    updated_by = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('Lastly updated by'), editable=False, blank=True, null=True)
    updates_count = models.PositiveIntegerField(verbose_name=_('Updates count'), editable=False, blank=True, default=0)

    class Meta:
        abstract = True
        ordering = ['created', ]
        get_latest_by = 'created'
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        app_label = 'conversation'

    def __unicode__(self):
        subject = '{}'.format(self.topic.subject)
        if self.topic.first_post != self:
            return machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX + subject
        return subject
