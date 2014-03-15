# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model

# Local application / specific library imports
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
ForumReadTrack = get_model('tracking', 'ForumReadTrack')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class TrackingHandler(object):
    def get_unread_forums(self, forums, user):
        """
        Returns a list of unread forums for the given user from a given
        set of forums.
        """
        unread_forums = []
        processed_forums = []

        # A user which is not authenticated will never see a forum as unread
        if not user.is_authenticated():
            return unread_forums

        # Forums are sorted by their position in the forums tree in order
        # to limit the number of operations required to determine the unread
        # forums below a forum which has the smallest position among the
        # forums from the initial set.
        # In fact, a forum is unread if at least one of its descendants
        # (including itself) is unread.
        # So the forums are sorted and then are processed by batches: from
        # a forum with a small level and all of its descendants, we get the
        # unread forums, and so on.
        sorted_forums = sorted(forums, key=lambda forum: forum.level)

        for forum in sorted_forums:
            if forum not in unread_forums and forum not in processed_forums:
                readable_forums = perm_handler.forum_list_filter(
                    forum.get_descendants(include_self=True), user)
                unread = ForumReadTrack.objects.get_unread_forums_from_list(readable_forums, user)
                unread_forums.extend(unread)
                processed_forums.extend(readable_forums)

        return unread_forums

    def get_unread_topics(self, topics, user):
        """
        Returns a list of unread topics for the given user from a given
        set of topics.
        """
        unread_topics = []

        # A user which is not authenticated will never see a topic as unread
        if not user.is_authenticated():
            return unread_topics

        # A topic can be unread if a track for itself exists with a mark time that
        # is less important than its update date.
        topic_tracks = TopicReadTrack.objects.filter(topic__in=topics, user=user)
        tracked_topics = topic_tracks.values_list('topic__pk', flat=True)

        if topic_tracks.exists():
            tracks_dict = dict(topic_tracks.values_list('topic__pk', 'mark_time'))
            for topic in topics:
                topic_last_modification_date = topic.updated or topic.created
                if topic.id in tracks_dict.keys() and topic_last_modification_date > tracks_dict[topic.id]:
                    unread_topics.append(topic)

        # A topic can be unread if a track for its associated forum exists with
        # a mark time that is less important than its creation or update date.
        forums = [topic.forum for topic in topics]
        forum_tracks = ForumReadTrack.objects.filter(forum__in=forums, user=user)
        tracked_forums = forum_tracks.values_list('forum__pk', flat=True)

        if forum_tracks.exists():
            tracks_dict = dict(forum_tracks.values_list('forum__pk', 'mark_time'))
            for topic in topics:
                topic_last_modification_date = topic.updated or topic.created
                if ((topic.forum.id in tracks_dict.keys() and topic.id not in tracked_topics) and
                        topic_last_modification_date > tracks_dict[topic.forum.id]):
                    unread_topics.append(topic)

        # A topic can be unread if no tracks exists for it
        for topic in topics:
            if topic.forum.pk not in tracked_forums and topic.pk not in tracked_topics:
                unread_topics.append(topic)

        return list(set(unread_topics))
