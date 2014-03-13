# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.apps.conversation.polls import validators
from machina.core.compat import AUTH_USER_MODEL
from machina.models.abstract_models import DatedModel


@python_2_unicode_compatible
class AbstractTopicPoll(DatedModel):
    """
    Represents a poll embedded in a forum topic.
    """
    topic = models.OneToOneField('conversation.Topic', verbose_name=_('Topic'), related_name='poll')

    # A poll can have a duration
    duration = models.PositiveIntegerField(verbose_name=_('Poll duration, in days'), blank=True, null=True)

    # Users can possibly select more than one option associated with a poll
    max_options = models.PositiveSmallIntegerField(
        verbose_name=_('Maximum number of poll options per user'),
        validators=[validators.validate_poll_max_options, ], default=1)

    # Are users allowed to change their votes ?
    user_changes = models.BooleanField(verbose_name=_('Allow vote changes'), default=False)

    class Meta:
        abstract = True
        ordering = ['-updated', ]
        get_latest_by = 'updated'
        verbose_name = _('Topic poll')
        verbose_name_plural = _('Topic polls')
        app_label = 'polls'

    def __str__(self):
        return '{}'.format(self.topic.subject)


@python_2_unicode_compatible
class AbstractTopicPollOption(models.Model):
    """
    Represents a poll option.
    """
    poll = models.ForeignKey('polls.TopicPoll', verbose_name=_('Poll'), related_name='options')
    text = models.CharField(max_length=255, verbose_name=_('Poll option text'))

    class Meta:
        abstract = True
        verbose_name = _('Topic poll option')
        verbose_name_plural = _('Topic poll options')
        app_label = 'polls'

    def __str__(self):
        return '{} - {}'.format(self.poll, self.text)


@python_2_unicode_compatible
class AbstractTopicPollVote(models.Model):
    """
    Represents a poll vote.
    """
    poll_option = models.ForeignKey('polls.TopicPollOption', verbose_name=_('Poll option'), related_name='votes')
    voter = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('Voter'), related_name='poll_votes')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Vote\'s date'))

    class Meta:
        abstract = True
        verbose_name = _('Topic poll vote')
        verbose_name_plural = _('Topic poll votes')
        app_label = 'polls'

    def __str__(self):
        return '{} - {}'.format(self.poll_option, self.voter)
