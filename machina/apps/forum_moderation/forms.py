# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.forms.widgets import SelectWithDisabled


Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class TopicMoveForm(forms.Form):
    forum = forms.ChoiceField(
        label=_('Select a destination forum'),
        widget=SelectWithDisabled)
    lock_topic = forms.BooleanField(
        label=_('Lock topic'), required=False)

    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('topic', None)
        self.user = kwargs.pop('user', None)
        self.perm_handler = PermissionHandler()

        super(TopicMoveForm, self).__init__(*args, **kwargs)

        self.allowed_forums = self.perm_handler.get_target_forums_for_moved_topics(self.user)
        forum_choices = []

        for f in self.allowed_forums:
            if f.is_category or f.id == self.topic.forum.id:
                forum_choices.append((
                    f.id,
                    {
                        'label': '{} {}'.format('-' * f.margin_level, f.name),
                        'disabled': True,
                    }))
            else:
                forum_choices.append((f.id, '{} {}'.format('-' * f.margin_level, f.name)))

        if self.topic.is_locked:
            self.fields['lock_topic'].initial = True

        self.fields['forum'].choices = forum_choices

    def clean_forum(self):
        forum_id = self.cleaned_data['forum']

        if forum_id:
            forum = Forum.objects.get(pk=forum_id)
            if forum.is_category or forum.is_link or forum.id == self.topic.forum.id:
                raise forms.ValidationError('You cannot select this forum as a destination')

        return forum
