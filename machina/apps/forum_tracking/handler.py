"""
    Forum tracking handler
    ======================

    This module defines a ``TrackingHandler`` abstraction that allows to identify unread forums and
    topics.

"""

from django.db.models import F, Q

from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class TrackingHandler:
    """ Provides utility methods to compute unread forums and topics.

    The TrackingHandler allows to filter list of forums and list of topics in order to get only the
    forums which contain unread topics or the unread topics.

    """

    def __init__(self, request=None):
        self.request = request
        self.perm_handler = request.forum_permission_handler if request \
            else PermissionHandler()

    def get_unread_forums(self, user):
        """ Returns the list of unread forums for the given user. """
        return self.get_unread_forums_from_list(
            user, self.perm_handler.get_readable_forums(Forum.objects.all(), user))

    def get_unread_forums_from_list(self, user, forums):
        """ Returns the list of unread forums for the given user from a given list of forums. """
        unread_forums = []

        # A user which is not authenticated will never see a forum as unread
        if not user.is_authenticated:
            return unread_forums

        unread = ForumReadTrack.objects.get_unread_forums_from_list(forums, user)
        unread_forums.extend(unread)

        return unread_forums

    def get_unread_topics(self, topics, user):
        """ Returns a list of unread topics for the given user from a given set of topics. """
        unread_topics = []

        # A user which is not authenticated will never see a topic as unread.
        # If there are no topics to consider, we stop here.
        if not user.is_authenticated or topics is None or not len(topics):
            return unread_topics

        # A topic can be unread if a track for itself exists with a mark time that
        # is less important than its update date.
        topic_ids = [topic.id for topic in topics]
        topic_tracks = TopicReadTrack.objects.filter(topic__in=topic_ids, user=user)
        tracked_topics = dict(topic_tracks.values_list('topic__pk', 'mark_time'))

        if tracked_topics:
            for topic in topics:
                topic_last_modification_date = topic.last_post_on or topic.created
                if (
                    topic.id in tracked_topics.keys() and
                    topic_last_modification_date > tracked_topics[topic.id]
                ):
                    unread_topics.append(topic)

        # A topic can be unread if a track for its associated forum exists with
        # a mark time that is less important than its creation or update date.
        forum_ids = [topic.forum_id for topic in topics]
        forum_tracks = ForumReadTrack.objects.filter(forum_id__in=forum_ids, user=user)
        tracked_forums = dict(forum_tracks.values_list('forum__pk', 'mark_time'))

        if tracked_forums:
            for topic in topics:
                topic_last_modification_date = topic.last_post_on or topic.created
                if (
                    (topic.forum_id in tracked_forums.keys() and topic.id not in tracked_topics) and
                    topic_last_modification_date > tracked_forums[topic.forum_id]
                ):
                    unread_topics.append(topic)

        # A topic can be unread if no tracks exists for it
        for topic in topics:
            if topic.forum_id not in tracked_forums and topic.id not in tracked_topics:
                unread_topics.append(topic)

        return list(set(unread_topics))

    def mark_forums_read(self, forums, user):
        """ Marks a list of forums as read. """
        if not forums or not user.is_authenticated:
            return

        forums = sorted(forums, key=lambda f: f.level)

        # Update all forum tracks to the current date for the considered forums
        for forum in forums:
            forum_track = ForumReadTrack.objects.get_or_create(forum=forum, user=user)[0]
            forum_track.save()
        # Delete all the unnecessary topic tracks
        TopicReadTrack.objects.filter(topic__forum__in=forums, user=user).delete()
        # Update parent forum tracks
        self._update_parent_forum_tracks(forums[0], user)

    def mark_topic_read(self, topic, user):
        """ Marks a topic as read. """
        if not user.is_authenticated:
            return

        forum = topic.forum
        try:
            forum_track = ForumReadTrack.objects.get(forum=forum, user=user)
        except ForumReadTrack.DoesNotExist:
            forum_track = None

        if (
            forum_track is None or
            (topic.last_post_on and forum_track.mark_time < topic.last_post_on)
        ):
            topic_track, created = TopicReadTrack.objects.get_or_create(topic=topic, user=user)
            if not created:
                topic_track.save()  # mark_time filled

            # If no other topic is unread inside the considered forum, the latter should also be
            # marked as read.
            unread_topics = (
                forum.topics
                .filter(
                    Q(tracks__user=user, tracks__mark_time__lt=F('last_post_on')) |
                    Q(
                        forum__tracks__user=user, forum__tracks__mark_time__lt=F('last_post_on'),
                        tracks__isnull=True,
                    )
                )
                .exclude(id=topic.id)
            )

            forum_topic_tracks = TopicReadTrack.objects.filter(topic__forum=forum, user=user)
            if (
                not unread_topics.exists() and
                (
                    forum_track is not None or
                    forum_topic_tracks.count() == forum.topics.filter(approved=True).count()
                )
            ):
                # The topics that are marked as read inside the forum for the given user will be
                # deleted while the forum track associated with the user must be created or updated.
                # This is done only if there are as many topic tracks as approved topics in case
                # the related forum has not beem previously marked as read.
                TopicReadTrack.objects.filter(topic__forum=forum, user=user).delete()
                forum_track, _ = ForumReadTrack.objects.get_or_create(forum=forum, user=user)
                forum_track.save()

                # Update parent forum tracks
                self._update_parent_forum_tracks(forum, user)

    def _update_parent_forum_tracks(self, forum, user):
        for forum in forum.get_ancestors(ascending=True):
            # If no other topics are unread inside the considered forum, the latter should also
            # be marked as read.
            unread_topics = (
                forum.topics
                .filter(
                    Q(tracks__user=user, tracks__mark_time__lt=F('last_post_on')) |
                    Q(
                        forum__tracks__user=user, forum__tracks__mark_time__lt=F('last_post_on'),
                        tracks__isnull=True,
                    ),
                )
            )
            if unread_topics.exists():
                break

            # The topics that are marked as read inside the forum for the given user
            # wil be deleted while the forum track associated with the user must be
            # created or updated.
            TopicReadTrack.objects.filter(topic__forum=forum, user=user).delete()
            forum_track, _ = ForumReadTrack.objects.get_or_create(forum=forum, user=user)
            forum_track.save()
