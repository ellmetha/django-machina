# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.dispatch import receiver

# Local application / specific library imports
from machina.core.loading import get_class
from machina.core.loading import get_classes

ForumReadTrack, TopicReadTrack = get_classes('forum_tracking.models',
                                             ['ForumReadTrack', 'TopicReadTrack'])

TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')
track_handler = TrackingHandler()

topic_viewed = get_class('forum_conversation.signals', 'topic_viewed')


@receiver(topic_viewed)
def update_user_trackers(sender, topic, user, request, response, **kwargs):
    """
    Receiver to mark a topic being viewed as read. This can result in marking
    the related forum tracker as read.
    """
    track_handler.mark_topic_read(topic, user)
