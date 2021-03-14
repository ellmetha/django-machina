"""
    Forum member abstract models
    ============================

    This module defines abstract models provided by the ``forum_member`` application.

"""

import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from machina.conf import settings as machina_settings
from machina.core import validators
from machina.models.fields import ExtendedImageField, MarkupTextField


def get_profile_avatar_upload_to(instance, filename):
    """ Returns a valid upload path for the avatar associated with a forum profile. """
    return instance.get_avatar_upload_to(filename)


class AbstractForumProfile(models.Model):
    """ Represents the profile associated with each forum user. """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_profile',
        verbose_name=_('User'),
    )

    # The user's avatar.
    avatar = ExtendedImageField(
        null=True, blank=True, upload_to=get_profile_avatar_upload_to, verbose_name=_('Avatar'),
        **machina_settings.DEFAULT_AVATAR_SETTINGS
    )

    # The user's signature.
    signature = MarkupTextField(
        verbose_name=_('Signature'), blank=True, null=True,
        validators=[
            validators.MarkupMaxLengthValidator(
                machina_settings.PROFILE_SIGNATURE_MAX_LENGTH
            ),
        ],
    )

    # The amount of posts the user has posted (only approved posts are considered here).
    posts_count = models.PositiveIntegerField(verbose_name=_('Total posts'), blank=True, default=0)

    class Meta:
        abstract = True
        app_label = 'forum_member'
        verbose_name = _('Forum profile')
        verbose_name_plural = _('Forum profiles')

    def __str__(self):
        return self.user.get_username()

    def get_avatar_upload_to(self, filename):
        """ Returns the path to upload the associated avatar to. """
        dummy, ext = os.path.splitext(filename)
        return os.path.join(
            machina_settings.PROFILE_AVATAR_UPLOAD_TO,
            '{id}{ext}'.format(id=str(uuid.uuid4()).replace('-', ''), ext=ext),
        )
