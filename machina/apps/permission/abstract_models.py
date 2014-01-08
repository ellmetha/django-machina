# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from guardian.models import GroupObjectPermissionBase
from guardian.models import UserObjectPermissionBase

# Local application / specific library imports


@python_2_unicode_compatible
class AbstractForumUserObjectPermission(UserObjectPermissionBase):
    """
    Represents a per-user forum object permission.
    The 'real' permission handling is part of django-guardian.
    """
    content_object = models.ForeignKey('forum.Forum', verbose_name=_('Forum'))

    class Meta:
        abstract = True
        verbose_name = _('User forum object permission')
        verbose_name_plural = _('User forum object permissions')
        app_label = 'permission'

    def __str__(self):
        return '{} - {}'.format(self.permission, self.content_object)


@python_2_unicode_compatible
class AbstractForumGroupObjectPermission(GroupObjectPermissionBase):
    """
    Represents a per-group forum object permission.
    The 'real' permission handling is part of django-guardian.
    """
    content_object = models.ForeignKey('forum.Forum', verbose_name=_('Forum'))

    class Meta:
        abstract = True
        verbose_name = _('Group forum object permission')
        verbose_name_plural = _('Group forum object permissions')
        app_label = 'permission'

    def __str__(self):
        return '{} - {}'.format(self.permission, self.content_object)
