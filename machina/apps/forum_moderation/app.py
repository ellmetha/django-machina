# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from machina.core.app import Application
from machina.core.loading import get_class


class ModerationApp(Application):
    name = 'forum_moderation'

    topic_lock_view = get_class('forum_moderation.views', 'TopicLockView')
    topic_unlock_view = get_class('forum_moderation.views', 'TopicUnlockView')
    topic_delete_view = get_class('forum_moderation.views', 'TopicDeleteView')
    topic_move_view = get_class('forum_moderation.views', 'TopicMoveView')
    topic_update_to_normal_topic_view = get_class(
        'forum_moderation.views', 'TopicUpdateToNormalTopicView')
    topic_update_to_sticky_topic_view = get_class(
        'forum_moderation.views', 'TopicUpdateToStickyTopicView')
    topic_update_to_announce_view = get_class('forum_moderation.views', 'TopicUpdateToAnnounceView')
    moderation_queue_list_view = get_class('forum_moderation.views', 'ModerationQueueListView')
    moderation_queue_detail_view = get_class('forum_moderation.views', 'ModerationQueueDetailView')
    post_approve_view = get_class('forum_moderation.views', 'PostApproveView')
    post_disapprove_view = get_class('forum_moderation.views', 'PostDisapproveView')

    def get_urls(self):
        return [
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/lock/$'),
                self.topic_lock_view.as_view(), name='topic_lock'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/unlock/$'),
                self.topic_unlock_view.as_view(), name='topic_unlock'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/delete/$'),
                self.topic_delete_view.as_view(), name='topic_delete'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/move/$'),
                self.topic_move_view.as_view(), name='topic_move'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/change/topic/$'),
                self.topic_update_to_normal_topic_view.as_view(), name='topic_update_to_post'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/change/sticky/$'),
                self.topic_update_to_sticky_topic_view.as_view(), name='topic_update_to_sticky'),
            url(_(r'^topic/(?P<slug>[\w-]+)-(?P<pk>\d+)/change/announce/$'),
                self.topic_update_to_announce_view.as_view(), name='topic_update_to_announce'),
            url(_(r'^queue/$'), self.moderation_queue_list_view.as_view(), name='queue'),
            url(_(r'^queue/(?P<pk>\d+)/$'),
                self.moderation_queue_detail_view.as_view(), name='queued_post'),
            url(_(r'^queue/(?P<pk>\d+)/approve/$'),
                self.post_approve_view.as_view(), name='approve_queued_post'),
            url(_(r'^queue/(?P<pk>\d+)/disapprove/$'),
                self.post_disapprove_view.as_view(), name='disapprove_queued_post'),
        ]


application = ModerationApp()
