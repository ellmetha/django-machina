# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F
from django.dispatch import receiver

from machina.apps.forum_conversation.signals import topic_viewed


@receiver(topic_viewed)
def update_topic_counter(sender, topic, user, request, response, **kwargs):
    """
    Receiver to handle the update of the views counter associated with topics.
    """
    topic.__class__._default_manager.filter(id=topic.id).update(views_count=F('views_count') + 1)
