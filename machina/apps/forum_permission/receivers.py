# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db.models import signals
from django.dispatch import receiver

# Local application / specific library imports
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


try:  # pragma: no cover
    from south import signals as south_signals

    @receiver(south_signals.post_migrate)
    def create_global_permissions_with_south(app, sender, **kwargs):
        if app == 'forum_permission':
            create_permissions()
except ImportError:  # pragma: no cover
    pass
