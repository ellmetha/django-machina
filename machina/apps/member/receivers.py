# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.db.models import F
from django.db.models.signals import pre_save

# Local application / specific library imports
from machina.core.db.models import get_model

Post = get_model('conversation', 'Post')
Profile = get_model('member', 'Profile')


def update_member_profile(sender, instance, **kwargs):
    """
    Receiver to handle the update of the profile related to the user
    who is the poster of the forum post being created or updated.
    """
    profile, dummy = Profile.objects.get_or_create(user=instance.poster)
    increase_posts_count = False

    if instance.pk:
        old_instance = instance.__class__._default_manager.get(pk=instance.pk)
        if old_instance.approved is False and instance.approved is True:
            increase_posts_count = True
    elif instance.approved:
        increase_posts_count = True

    if increase_posts_count:
        profile.posts_count = F('posts_count') + 1
        profile.save()


pre_save.connect(update_member_profile, sender=Post)
