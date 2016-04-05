# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class AbstractForumPermission(models.Model):
    """
    Represents a single forum permission.
    """
    codename = models.CharField(max_length=150, verbose_name=_('Permission codename'), unique=True)
    name = models.CharField(
        max_length=255, verbose_name=_('Permission name'), blank=True, null=True)

    is_global = models.BooleanField(
        verbose_name=_('Global permission'),
        help_text=_('This permission can be granted globally to all the forums'),
        default=False)
    is_local = models.BooleanField(
        verbose_name=_('Local permission'),
        help_text=_('This permission can be granted individually for each forum'),
        default=True)

    class Meta:
        abstract = True
        app_label = 'forum_permission'
        verbose_name = _('Forum permission')
        verbose_name_plural = _('Forum permissions')

    def __str__(self):
        if self.name:
            return '{} - {}'.format(self.codename, self.name)
        return self.codename

    def clean(self):
        super(AbstractForumPermission, self).clean()
        if not self.is_global and not self.is_local:
            raise ValidationError(_('A forum permission should be at least either global or local'))


class BaseAuthForumPermission(models.Model):
    """
    Represents a per-auth-component forum object permission.
    """
    permission = models.ForeignKey(
        'forum_permission.ForumPermission', verbose_name=_('Forum permission'))
    has_perm = models.BooleanField(verbose_name=_('Has perm'), default=True)

    # The forum related to a UserForumPermission instance can be null if the
    # considered permission should be granted globally.
    forum = models.ForeignKey('forum.Forum', verbose_name=_('Forum'), blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        super(BaseAuthForumPermission, self).clean()
        if self.forum is None and not self.permission.is_global:
            raise ValidationError(
                _('The following permission cannot be granted globally: {}'.format(
                    self.permission)))


@python_2_unicode_compatible
class AbstractUserForumPermission(BaseAuthForumPermission):
    """
    Represents a per-user forum object permission.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'), null=True, blank=True)
    anonymous_user = models.BooleanField(verbose_name=_('Target anonymous user'), default=False)

    class Meta:
        abstract = True
        unique_together = ('permission', 'forum', 'user', )
        app_label = 'forum_permission'
        verbose_name = _('User forum permission')
        verbose_name_plural = _('User forum permissions')

    def __str__(self):
        if self.forum:
            return '{} - {} - {}'.format(self.permission, self.user, self.forum)
        return '{} - {}'.format(self.permission, self.user)

    def clean(self):
        super(AbstractUserForumPermission, self).clean()
        if (self.user is None and not self.anonymous_user) \
                or (self.user and self.anonymous_user):
            raise ValidationError(
                _('A permission should target either a user or an anonymous user'))


@python_2_unicode_compatible
class AbstractGroupForumPermission(BaseAuthForumPermission):
    """
    Represents a per-group forum object permission.
    """
    group = models.ForeignKey(Group, verbose_name=_('Group'))

    class Meta:
        abstract = True
        unique_together = ('permission', 'forum', 'group', )
        app_label = 'forum_permission'
        verbose_name = _('Group forum permission')
        verbose_name_plural = _('Group forum permissions')

    def __str__(self):
        if self.forum:
            return '{} - {} - {}'.format(self.permission, self.group, self.forum)
        return '{} - {}'.format(self.permission, self.group)
