# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F
from django.db.models import Q

from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')
Topic = get_model('forum_conversation', 'Topic')
Post = get_model('forum_conversation', 'Post')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')


class TrackingHandler(object):
    """
    The TrackingHandler allows to filter list of forums and list of topics
    in order to get only the forums which contain unread topics or the unread
    topics.
    """

    def __init__(self, request=None):
        self.request = request
        self.perm_handler = request.forum_permission_handler if request \
            else PermissionHandler()

    def get_unread_forums(self, user):
        """
        Returns the list of unread forums for the given user.
        """
        unread_forums = []

        # A user which is not authenticated will never see a forum as unread
        if not user.is_authenticated():
            return unread_forums

        readable_forums = self.perm_handler.get_readable_forums(Forum.objects.all(), user)
        unread = ForumReadTrack.objects.get_unread_forums_from_list(readable_forums, user)
        unread_forums.extend(unread)

        return unread_forums

    def get_unread_topics(self, topics, user):
        """
        Returns a list of unread topics for the given user from a given
        set of topics.
        """

        # A user which is not authenticated will never see a topic as unread.
        # If there are no topics to consider, we stop here.
        if not user.is_authenticated() or topics is None or not len(topics):
            return []

        topic_ids = [topic.id for topic in topics]

        # build query constraints

        in_topics = Q(id__in=topic_ids)

        updated_after_last_read_topic = (Q(tracks__user=user)
                                         & (Q(tracks__mark_time__lt=F('last_post_on'))
                                            | (Q(tracks__mark_time__lt=F('created')))))

        updated_after_last_read_forum = (Q(forum__tracks__user=user)
                                         & (Q(forum__tracks__mark_time__lt=F('last_post_on'))
                                            | (Q(forum__tracks__mark_time__lt=F('created')))))

        updated_before_last_read_topic = (Q(tracks__user=user)
                                          & (Q(tracks__mark_time__gte=F('last_post_on'))
                                             | (Q(tracks__mark_time__gte=F('created')))))

        untracked = (~Q(tracks__user=self.request.user) & ~Q(forum__tracks__user=user))

        untracked_ids = Topic.approved_objects.filter(in_topics & untracked).values_list('id', flat=True)

        not_tracked = Q(id__in=untracked_ids)

        # run query
        unread_topics = Topic.approved_objects.filter(in_topics & ((updated_after_last_read_topic
                                                           | (updated_after_last_read_forum
                                                              & ~updated_before_last_read_topic))
                                                          | not_tracked))

        return unread_topics

    def get_oldest_unread_post(self, topic, user):

        if not user.is_authenticated() or topic is None:
            return None

        read_posts = Post.approved_objects.filter(Q(topic=topic)
                                                  & Q(topic__tracks__mark_time__gte=F('created'))
                                                  ).values_list("id", flat=True)

        unread_posts = Post.approved_objects.filter(Q(topic=topic)
                                                    & (Q(topic__tracks__mark_time__lt=F('created'))
                                                       | (Q(topic__forum__tracks__mark_time__lt=F('created'))
                                                          & ~Q(id__in=read_posts)))
                                                    ).order_by('created')[:1]

        if unread_posts:
            return unread_posts[0].pk
        else:
            return None

    def mark_forums_read(self, forums, user):
        """
        Marks a list of forums as read.
        """
        if not forums or not user.is_authenticated():
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
        """
        Marks a topic as read.
        """
        if not user.is_authenticated():
            return

        forum = topic.forum
        try:
            forum_track = ForumReadTrack.objects.get(forum=forum, user=user)
        except ForumReadTrack.DoesNotExist:
            forum_track = None

        if forum_track is None \
            or (topic.last_post_on and forum_track.mark_time < topic.last_post_on):
            topic_track, created = TopicReadTrack.objects.get_or_create(topic=topic, user=user)
            if not created:
                topic_track.save()  # mark_time filled

            # If no other topic is unread inside the considered forum, the latter should also be
            # marked as read.
            unread_topics = forum.topics.filter(
                Q(tracks__user=user, tracks__mark_time__lt=F('last_post_on')) |
                Q(forum__tracks__user=user, forum__tracks__mark_time__lt=F('last_post_on'),
                  tracks__isnull=True)).exclude(id=topic.id)

            forum_topic_tracks = TopicReadTrack.objects.filter(topic__forum=forum, user=user)
            if not unread_topics.exists() and (
                        forum_track is not None or
                        forum_topic_tracks.count() == forum.topics.filter(approved=True).count()):
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
            unread_topics = forum.topics.filter(
                Q(tracks__user=user, tracks__mark_time__lt=F('last_post_on')) |
                Q(forum__tracks__user=user, forum__tracks__mark_time__lt=F('last_post_on'),
                  tracks__isnull=True))
            if unread_topics.exists():
                break

            # The topics that are marked as read inside the forum for the given user
            # wil be deleted while the forum track associated with the user must be
            # created or updated.
            TopicReadTrack.objects.filter(topic__forum=forum, user=user).delete()
            forum_track, _ = ForumReadTrack.objects.get_or_create(forum=forum, user=user)
            forum_track.save()
