# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'content', ]

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)


class TopicForm(PostForm):
    topic_type = forms.ChoiceField(label=_('Post topic as'), choices=Topic.TYPE_CHOICES)
