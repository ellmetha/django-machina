# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.shortcuts import get_object_or_none


TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollOption = get_model('forum_polls', 'TopicPollOption')


class TopicPollOptionForm(forms.ModelForm):
    class Meta:
        model = TopicPollOption
        fields = ['text', ]

    def __init__(self, *args, **kwargs):
        super(TopicPollOptionForm, self).__init__(*args, **kwargs)

        # Update the 'text' field
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['placeholder'] = _('Enter a poll option')
        self.fields['text'].required = False


class BaseTopicPollOptionFormset(BaseModelFormSet):
    topic = None
    poll = None

    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('topic', None)
        if self.topic:
            self.poll = get_object_or_none(TopicPoll, topic=self.topic)

        super(BaseTopicPollOptionFormset, self).__init__(*args, **kwargs)

        if self.poll is not None:
            for form in self.forms:
                form.instance.poll = self.poll

    def total_form_count(self):
        """
        This rewrite of total_form_count allows to add an empty form to the formset only when
        no initial data is provided.
        """
        total_forms = super(BaseTopicPollOptionFormset, self).total_form_count()
        if not self.data and not self.files and self.initial_form_count() > 0:
            total_forms -= self.extra
        return total_forms

    def clean(self):
        if any(self.errors):
            return

        # At least two options must be defined
        number_of_options = 0
        for form in self.forms:
            if not ((self.can_delete and self._should_delete_form(form)) or
                    len(form.cleaned_data) == 0):
                number_of_options += 1
        if number_of_options < 2:
            raise forms.ValidationError('At least two poll options must be defined.')

    def save(self, commit=True, **kwargs):
        poll_question = kwargs.pop('poll_question', None)
        poll_max_options = kwargs.pop('poll_max_options', None)
        poll_duration = kwargs.pop('poll_duration', None)
        poll_user_changes = kwargs.pop('poll_user_changes', False)

        if self.poll is None:
            poll, _ = TopicPoll.objects.get_or_create(topic=self.topic)

            poll.question = poll_question
            poll.duration = poll_duration
            poll.max_options = poll_max_options
            poll.user_changes = poll_user_changes
            poll.save()

            for form in self.forms:
                form.instance.poll = poll
        super(BaseTopicPollOptionFormset, self).save(commit)


TopicPollOptionFormset = modelformset_factory(
    TopicPollOption, TopicPollOptionForm,
    formset=BaseTopicPollOptionFormset,
    can_delete=True, extra=2, max_num=machina_settings.POLL_MAX_OPTIONS_PER_POLL,
    validate_max=True)


class TopicPollVoteForm(forms.Form):
    def __init__(self, poll, *args, **kwargs):
        self.poll = poll
        super(TopicPollVoteForm, self).__init__(*args, **kwargs)

        if poll.max_options == 1:
            self.fields['options'] = forms.ModelChoiceField(
                label='', queryset=poll.options.all(), empty_label=None,
                widget=forms.RadioSelect())
        else:
            self.fields['options'] = forms.ModelMultipleChoiceField(
                label='', queryset=poll.options.all(),
                widget=forms.CheckboxSelectMultiple())

    def clean_options(self):
        options = self.cleaned_data['options']
        if isinstance(options, TopicPollOption):
            options = [options, ]
        return options

    def clean(self):
        cleaned_data = super(TopicPollVoteForm, self).clean()

        if 'options' not in cleaned_data:
            msg = _('You must specify an option when voting.')
            raise ValidationError(msg)

        options = cleaned_data['options']
        if len(options) > self.poll.max_options:
            msg = _('You have tried to vote for too many options.')
            raise ValidationError(msg)

        return cleaned_data
