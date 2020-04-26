"""
    Forum permission abstract models
    ================================

    This module defines abstract models provided by the ``forum_permission`` application.

"""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from machina.core.loading import get_class


PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


class AbstractForumPermission(models.Model):
    """ Represents a single forum permission.

    The models that subclass ``AbstractForumPermission`` can be used to define forum permissions. A
    forum permission is basically defined by a codename and some booleans indicating if the
    considered permission can be granted globally (in that case the permission applies to all
    forums) or not.

    """

    codename = models.CharField(
        max_length=150, verbose_name=_('Permission codename'), unique=True, db_index=True,
    )

    class Meta:
        abstract = True
        app_label = 'forum_permission'
        verbose_name = _('Forum permission')
        verbose_name_plural = _('Forum permissions')

    def __str__(self):
        return '{} - {}'.format(self.codename, self.name)

    @cached_property
    def name(self):
        """ Returns the name of the considered permission. """
        perm_config = PermissionConfig().get(self.codename)
        return perm_config['label'] if perm_config else None


class BaseAuthForumPermission(models.Model):
    """ Represents a per-auth-component forum object permission. """

    permission = models.ForeignKey(
        'forum_permission.ForumPermission', on_delete=models.CASCADE,
        verbose_name=_('Forum permission'),
    )
    has_perm = models.BooleanField(verbose_name=_('Has perm'), default=True, db_index=True)

    # The forum related to a UserForumPermission instance can be null if the considered permission
    # should be granted globally.
    forum = models.ForeignKey(
        'forum.Forum', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Forum'),
    )

    class Meta:
        abstract = True


class AbstractUserForumPermission(BaseAuthForumPermission):
    """ Represents a per-user forum object permission. """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    anonymous_user = models.BooleanField(
        verbose_name=_('Target anonymous user'), default=False, db_index=True,
    )
    authenticated_user = models.BooleanField(
        verbose_name=_('Target any logged in user'), default=False, db_index=True,
    )

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
        """ Validates the current instance. """
        super().clean()
        if (
            (self.user is None and not self.anonymous_user and not self.authenticated_user) or
            ((self.user and self.anonymous_user) or (self.user and self.authenticated_user) or
             (self.anonymous_user and self.authenticated_user))
        ):
            raise ValidationError(
                _(
                    "A permission should target either a specific user, an anonymous user " +
                    "or any authenticated user"
                ),
            )


class AbstractGroupForumPermission(BaseAuthForumPermission):
    """ Represents a per-group forum object permission. """

    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Group'))

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
