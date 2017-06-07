# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from machina.core.db.models import get_model
from machina.core.loading import get_class


ForumPermission = get_model('forum_permission', 'ForumPermission')
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
