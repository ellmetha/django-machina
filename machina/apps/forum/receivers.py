"""
    Forum signal receivers
    ======================

    This module defines signal receivers.

"""

from django.db.models import F
from django.dispatch import receiver

from machina.apps.forum.signals import forum_viewed


@receiver(forum_viewed)
def update_forum_redirects_counter(sender, forum, user, request, response, **kwargs):
    """ Handles the update of the link redirects counter associated with link forums. """
    if forum.is_link and forum.link_redirects:
        forum.link_redirects_count = F('link_redirects_count') + 1
        forum.save()
