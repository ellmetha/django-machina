# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import forms
from django.db.models import get_model

# Local application / specific library imports

Post = get_model('conversation', 'Post')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'content', ]

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
