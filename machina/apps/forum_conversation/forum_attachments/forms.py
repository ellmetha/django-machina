# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.forms.models import BaseModelFormSet
from django.forms.models import modelformset_factory

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model


Attachment = get_model('forum_attachments', 'Attachment')


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
    can_delete=True, extra=1,
    max_num=machina_settings.ATTACHMENT_MAX_FILES_PER_POST,
    validate_max=True)
