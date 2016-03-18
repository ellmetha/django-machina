# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms

from machina.core.db.models import get_model

ForumProfile = get_model('forum_member', 'ForumProfile')


class ForumProfileForm(forms.ModelForm):
    class Meta:
        model = ForumProfile
        fields = ['avatar', 'signature', ]
