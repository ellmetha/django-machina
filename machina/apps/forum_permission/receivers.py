# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db.models import signals
from django.dispatch import receiver

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.compat import get_user_model
from machina.core.loading import get_class

ForumPermission = get_class('forum_permission.models', 'ForumPermission')
PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


def create_permissions():
    for config in PermissionConfig.permissions:
        try:
            gp = ForumPermission.objects.get(codename=config['codename'])
        except ForumPermission.DoesNotExist:
            gp = ForumPermission(**config)
        gp.save()


@receiver(signals.post_syncdb)
def create_global_permissions(app, sender, **kwargs):
    if app.__name__.endswith('forum_permission.models'):
        create_permissions()


@receiver(signals.post_syncdb)
def create_anonymous_user(app, sender, **kwargs):
    """
    Creates the anonymous user instance.
    """
    user_model = get_user_model()
    try:
        user_model.objects.get(pk=machina_settings.ANONYMOUS_USER_ID)
    except user_model.DoesNotExist:
        user_model.objects.create(**machina_settings.ANONYMOUS_USER_KWARGS)


try:  # pragma: no cover
    from south import signals as south_signals

    @receiver(south_signals.post_migrate)
    def create_global_permissions_with_south(app, sender, **kwargs):
        if app == 'forum_permission':
            create_permissions()
except ImportError:  # pragma: no cover
    pass
