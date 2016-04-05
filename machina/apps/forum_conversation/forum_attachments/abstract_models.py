# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from machina.conf import settings as machina_settings


@python_2_unicode_compatible
class AbstractAttachment(models.Model):
    """
    Represents a post attachment. An attachment is always linked to a post.
    """
    post = models.ForeignKey(
        'forum_conversation.Post', verbose_name=_('Post'), related_name='attachments')
    file = models.FileField(
        verbose_name=_('File'), upload_to=machina_settings.ATTACHMENT_FILE_UPLOAD_TO)
    comment = models.CharField(max_length=255, verbose_name=_('Comment'), blank=True, null=True)

    class Meta:
        abstract = True
        app_label = 'forum_attachments'
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __str__(self):
        return '{}'.format(self.post.subject)

    @property
    def filename(self):
        return os.path.basename(self.file.name)
