# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Local application / specific library imports
from machina.core.loading import get_class

Post = get_class('forum_conversation.models', 'Post')
Profile = get_class('forum_member.models', 'Profile')


@receiver(pre_save, sender=Post)
def update_member_profile(sender, instance, **kwargs):
    """
    Receiver to handle the update of the profile related to the user
    who is the poster of the forum post being created or updated.
    """
    profile, dummy = Profile.objects.get_or_create(user=instance.poster)
    increase_posts_count = False

    if instance.pk:
        try:
            old_instance = instance.__class__._default_manager.get(pk=instance.pk)
        except ObjectDoesNotExist:  # pragma: no cover
            # This should never happen (except with django loaddata command)
            increase_posts_count = True
            old_instance = None
        if old_instance and old_instance.approved is False and instance.approved is True:
            increase_posts_count = True
    elif instance.approved:
        increase_posts_count = True

    if increase_posts_count:
        profile.posts_count = F('posts_count') + 1
        profile.save()
