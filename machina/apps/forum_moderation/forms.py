# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.forms.widgets import SelectWithDisabled

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class TopicMoveForm(forms.Form):
    forum = forms.ChoiceField(
        label=_('Select a destination forum'),
        required=False, widget=SelectWithDisabled)
    lock_topic = forms.BooleanField(
        label=_('Lock topic'), required=False)

    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('instance', None)
        self.user = kwargs.pop('user', None)

        super(TopicMoveForm, self).__init__(*args, **kwargs)

        self.allowed_forums = perm_handler.forum_list_filter(Forum.objects.all(), self.user)
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

        if self.allowed_forums:
            self.fields['forum'].choices = forum_choices
        else:
            # The user cannot view any single forum, the 'forum' field can be deleted
            del self.fields['forum']

    def clean_forum(self):
        forum_id = self.cleaned_data['forum']

        if forum_id:
            forum = Forum.objects.get(pk=forum_id)
            if forum.is_category or forum.id == self.topic.forum.id:
                raise forms.ValidationError('You cannot select this forum as a destination')

        return forum
