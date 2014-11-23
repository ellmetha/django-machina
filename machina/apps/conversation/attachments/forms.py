# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import forms
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory
from django.db.models import get_model

# Local application / specific library imports

Attachment = get_model('attachments', 'Attachment')


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'comment', ]


class BaseAttachmentFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        super(BaseAttachmentFormset, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if self.post:
            for form in self.forms:
                form.instance.post = self.post
        super(BaseAttachmentFormset, self).save(commit)


AttachmentFormset = modelformset_factory(
    Attachment, AttachmentForm,
    formset=BaseAttachmentFormset,
    can_delete=True, extra=1)
