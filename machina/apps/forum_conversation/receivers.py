"""
    Forum conversation signal receivers
    ===================================

    This module defines signal receivers.

"""

from django.db.models import F
from django.dispatch import receiver

from machina.apps.forum_conversation.signals import topic_viewed


@receiver(topic_viewed)
def update_topic_counter(sender, topic, user, request, response, **kwargs):
    """ Handles the update of the views counter associated with topics. """
    topic.__class__._default_manager.filter(id=topic.id).update(views_count=F('views_count') + 1)
