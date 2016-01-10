# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Local application / specific library imports
from machina.core.loading import get_class

ForumPermission = get_class('forum_permission.models', 'ForumPermission')
PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


def create_permissions():
    for config in PermissionConfig.permissions:
        try:
            gp = ForumPermission.objects.get(codename=config['fields']['codename'])
        except ForumPermission.DoesNotExist:
            gp = ForumPermission(**config['fields'])
        gp.save()


@receiver(post_migrate)
def create_global_permissions(sender, **kwargs):
    if sender.name.endswith('forum_permission'):
        create_permissions()
