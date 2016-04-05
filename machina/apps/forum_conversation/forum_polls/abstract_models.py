# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from machina.apps.forum_conversation.forum_polls import validators
from machina.models.abstract_models import DatedModel


@python_2_unicode_compatible
class AbstractTopicPoll(DatedModel):
    """
    Represents a poll embedded in a forum topic.
    """
    topic = models.OneToOneField(
        'forum_conversation.Topic', verbose_name=_('Topic'), related_name='poll')

    # A poll is defined by a single question
    question = models.CharField(max_length=255, verbose_name=_('Poll question'))

    # A poll can have a duration
    duration = models.PositiveIntegerField(
        verbose_name=_('Poll duration, in days'), blank=True, null=True)

    # Users can possibly select more than one option associated with a poll
    max_options = models.PositiveSmallIntegerField(
        verbose_name=_('Maximum number of poll options per user'),
        validators=validators.poll_max_options, default=1)

    # Are users allowed to change their votes ?
    user_changes = models.BooleanField(verbose_name=_('Allow vote changes'), default=False)

    class Meta:
        abstract = True
        app_label = 'forum_polls'
        ordering = ['-updated', ]
        get_latest_by = 'updated'
        verbose_name = _('Topic poll')
        verbose_name_plural = _('Topic polls')

    def __str__(self):
        return '{}'.format(self.topic.subject)

    @cached_property
    def votes(self):
        """
        Returns all the votes related to this topic poll.
        """
        votes = []
        for option in self.options.all():
            votes += option.votes.all()
        return votes


@python_2_unicode_compatible
class AbstractTopicPollOption(models.Model):
    """
    Represents a poll option.
    """
    poll = models.ForeignKey(
        'forum_polls.TopicPoll', verbose_name=_('Poll'), related_name='options')
    text = models.CharField(max_length=255, verbose_name=_('Poll option text'))

    class Meta:
        abstract = True
        app_label = 'forum_polls'
        verbose_name = _('Topic poll option')
        verbose_name_plural = _('Topic poll options')

    def __str__(self):
        return '{} - {}'.format(self.poll, self.text)

    @property
    def percentage(self):
        if not hasattr(self, '_percentage'):
            self._percentage = (self.votes.count() / (len(self.poll.votes) or 1)) * 100
        return self._percentage


@python_2_unicode_compatible
class AbstractTopicPollVote(models.Model):
    """
    Represents a poll vote.
    """
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Voter'), related_name='poll_votes',
        blank=True, null=True)
    anonymous_key = models.CharField(
        max_length=100, verbose_name=_('Anonymous user forum key'), blank=True, null=True)

    poll_option = models.ForeignKey(
        'forum_polls.TopicPollOption', verbose_name=_('Poll option'), related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Vote\'s date'))

    class Meta:
        abstract = True
        app_label = 'forum_polls'
        verbose_name = _('Topic poll vote')
        verbose_name_plural = _('Topic poll votes')

    def __str__(self):
        return '{} - {}'.format(self.poll_option, self.voter)

    def clean(self):
        super(AbstractTopicPollVote, self).clean()

        # At least a poster (user) or a session key must be associated with
        # the vote instance.
        if self.voter is None and self.anonymous_key is None:
            raise ValidationError(_('A user id or an anonymous key must be used.'))
        if self.voter and self.anonymous_key:
            raise ValidationError(_('A user id or an anonymous key must be used, but not both.'))
