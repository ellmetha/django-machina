"""
    Forum permission signal receivers
    =================================

    This module defines signal receivers.

"""

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from machina.core.db.models import get_model
from machina.core.loading import get_class


ForumPermission = get_model('forum_permission', 'ForumPermission')
PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


def create_permissions():
    """ Creates all the permissions from the permission configuration. """
    for config in PermissionConfig.permissions:
        ForumPermission.objects.get_or_create(codename=config['codename'])


@receiver(post_migrate)
def create_global_permissions(sender, **kwargs):
    """ Creates all the permissions from the permission configuration during migrations. """
    if sender.name.endswith('forum_permission'):
        create_permissions()
