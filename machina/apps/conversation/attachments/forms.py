# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import forms
from django.forms.formsets import TOTAL_FORM_COUNT
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

        if self.post is not None:
            for form in self.forms:
                form.instance.post = self.post

    def total_form_count(self):
        """
        This rewrite of total_form_count allows to add an empty form to the formset only when
        no initial data is provided.
        """
        if self.data or self.files:
            return self.management_form.cleaned_data[TOTAL_FORM_COUNT]
        else:
            if self.initial_form_count() > 0:
                total_forms = self.initial_form_count()
            else:
                total_forms = self.initial_form_count() + self.extra
            if total_forms > self.max_num > 0:
                total_forms = self.max_num
            return total_forms

    def save(self, commit=True, **kwargs):
        if self.post:
            for form in self.forms:
                form.instance.post = self.post
        super(BaseAttachmentFormset, self).save(commit)


AttachmentFormset = modelformset_factory(
    Attachment, AttachmentForm,
    formset=BaseAttachmentFormset,
    can_delete=True, extra=1)
