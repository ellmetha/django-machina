"""
    Forum attachments abstract models
    =================================

    This module defines abstract models provided by the ``forum_attachments`` application.

"""

import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from machina.conf import settings as machina_settings


def get_attachment_file_upload_to(instance, filename):
    """ Returns a valid upload path for the file of an attachment. """
    return instance.get_file_upload_to(filename)


class AbstractAttachment(models.Model):
    """ Represents a post attachment. An attachment is always linked to a post. """

    post = models.ForeignKey(
        'forum_conversation.Post', related_name='attachments', on_delete=models.CASCADE,
        verbose_name=_('Post'),
    )
    file = models.FileField(upload_to=get_attachment_file_upload_to, verbose_name=_('File'))
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
        """ Returns the filename of the considered attachment. """
        return os.path.basename(self.file.name)

    def get_file_upload_to(self, filename):
        """ Returns the path to upload the associated file to. """
        return os.path.join(machina_settings.ATTACHMENT_FILE_UPLOAD_TO, filename)
