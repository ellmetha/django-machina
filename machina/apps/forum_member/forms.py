# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import forms

# Local application / specific library imports
from machina.core.db.models import get_model

ForumProfile = get_model('forum_member', 'ForumProfile')


class ForumProfileForm(forms.ModelForm):
    class Meta:
        model = ForumProfile
        fields = ['avatar', 'signature', ]
