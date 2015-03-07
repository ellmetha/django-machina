# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import F
from django.db.models import Q
from django.dispatch import receiver

# Local application / specific library imports
from machina.core.loading import get_class
from machina.core.loading import get_classes

ForumReadTrack, TopicReadTrack = get_classes('forum_tracking.models',
                                             ['ForumReadTrack', 'TopicReadTrack'])

topic_viewed = get_class('forum_conversation.signals', 'topic_viewed')


@receiver(topic_viewed)
def update_user_trackers(sender, topic, user, request, response, **kwargs):
    """
    Receiver to mark a topic being viewed as read. This can result in marking
    the related forum tracker as read.
    """
    if not user.is_authenticated():
        return

    forum = topic.forum
    try:
        forum_track = ForumReadTrack.objects.get(forum=forum, user=user)
    except ForumReadTrack.DoesNotExist:
        forum_track = None

    if forum_track is None or (topic.last_post_on and forum_track.mark_time < topic.last_post_on):
        topic_track, created = TopicReadTrack.objects.get_or_create(topic=topic, user=user)
        if not created:
            topic_track.save()  # mark_time filled

        # If no other topic is unread inside the considered forum, the latter should also
        # be marked as read.
        unread_topics = forum.topics.filter(
            Q(tracks__user=user, tracks__mark_time__lt=F('last_post_on')) |
            Q(forum__tracks__user=user, forum__tracks__mark_time__lt=F('last_post_on'), tracks__isnull=True)).exclude(id=topic.id)

        if not unread_topics.exists():
            # The topics that are marked as read inside the forum for the given user
            # wil be deleted while the forum track associated with the user must be
            # created or updated.
            TopicReadTrack.objects.filter(topic__forum=forum, user=user).delete()
            forum_track, _ = ForumReadTrack.objects.get_or_create(forum=forum, user=user)
            forum_track.save()
