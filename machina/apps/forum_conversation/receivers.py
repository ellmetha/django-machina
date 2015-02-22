# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import F
from django.dispatch import receiver

# Local application / specific library imports
from machina.apps.forum_conversation.signals import topic_viewed


@receiver(topic_viewed)
def update_topic_counter(sender, topic, user, request, response, **kwargs):
    """
    Receiver to handle the update of the views counter associated with topics.
    """
    topic.__class__._default_manager.filter(id=topic.id).update(views_count=F('views_count') + 1)
