# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.messages import constants as MSG
from django.core.urlresolvers import reverse
from django.db.models import get_model
from faker import Factory as FakerFactory
from guardian.shortcuts import assign_perm
from guardian.utils import get_anonymous_user

# Local application / specific library imports
from machina.apps.conversation.abstract_models import TOPIC_TYPES
from machina.apps.conversation.polls.forms import TopicPollOptionFormset
from machina.apps.conversation.polls.forms import TopicPollVoteForm
from machina.apps.conversation.signals import topic_viewed
from machina.core.loading import get_class
from machina.core.utils import refresh
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicReadTrackFactory
from machina.test.testcases import BaseClientTestCase
from machina.test.utils import mock_signal_receiver

faker = FakerFactory.create()

ForumReadTrack = get_model('tracking', 'ForumReadTrack')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')
TopicReadTrack = get_model('tracking', 'TopicReadTrack')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')


class TestTopicPollVoteView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicPollVoteView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Creates a poll and two options
        self.poll = TopicPollFactory.create(topic=self.topic)
        self.option_1 = TopicPollOptionFactory.create(poll=self.poll)
        self.option_2 = TopicPollOptionFactory.create(poll=self.poll)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_vote_in_polls', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('conversation:topic-poll-vote', kwargs={
            'forum_pk': self.top_level_forum.pk, 'topic_pk': self.topic.pk,
            'pk': self.poll.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        self.assertIsOk(response)
