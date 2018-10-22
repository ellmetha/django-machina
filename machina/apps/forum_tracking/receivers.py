"""
    Forum tracking signal receivers
    ===============================

    This module defines signal receivers.

"""

from django.dispatch import receiver

from machina.core.loading import get_class


topic_viewed = get_class('forum_conversation.signals', 'topic_viewed')


@receiver(topic_viewed)
def update_user_trackers(sender, topic, user, request, response, **kwargs):
    """ Receiver to mark a topic being viewed as read.

    This can result in marking the related forum tracker as read.

    """
    TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')  # noqa
    track_handler = TrackingHandler()
    track_handler.mark_topic_read(topic, user)
