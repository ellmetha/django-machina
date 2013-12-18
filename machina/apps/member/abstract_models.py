# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.compat import AUTH_USER_MODEL
from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField


class AbstractProfile(models.Model):
    """
    Represents the profile associated with each forum user.
    """
    user = models.OneToOneField(AUTH_USER_MODEL, verbose_name=_('User'), related_name='forum_profile')

    # The user's avatar
    avatar = ExtendedImageField(verbose_name=_('Avatar'), null=True, blank=True,
                                upload_to=machina_settings.PROFILE_AVATAR_UPLOAD_TO,
                                **machina_settings.DEFAULT_AVATAR_SETTINGS)

    # The user's signature
    signature = MarkupTextField(verbose_name=_('Signature'), max_length=machina_settings.SIGNATURE_MAX_LENGTH, blank=True, null=True)

    # The user's rank
    rank = models.ForeignKey('member.Rank', verbose_name=_('Rank'), blank=True, null=True)

    # The amount of posts the user has posted
    posts_count = models.PositiveIntegerField(verbose_name=_('Total posts'), blank=True, default=0)

    class Meta:
        abstract = True
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        app_label = 'member'

    def __unicode__(self):
        return '{} profile'.format(self.user.username)


class AbstractRank(models.Model):
    """
    Represents a rank that can be associated with any forum profile.
    """
    title = models.ChareField(max_length=100, verbose_name=_('Title'))
    image = models.ImageField(verbose_name=_('Rank image'), null=True, blank=True, upload_to=machina_settings.PROFILE_RANK_IMAGE_UPLOAD_TO)

    # Number of posts necessary to reach the rank
    min_posts = models.PositiveIntegerField(verbose_name=_('Minimum post count required'), blank=True, null=True)

    # A rank can be special ; if so only administrators will be able to add users to this rank manually
    is_special = models.BooleanField(verbose_name=_('Special rank'), default=False, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _('Rank')
        verbose_name_plural = _('Ranks')
        app_label = 'member'

    def __unicode__(self):
        return '{} rank'.format(self.title)
