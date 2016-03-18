# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from faker import Factory as FakerFactory
import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicPollVoteFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')


class TestTopicPollVoteView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Creates a poll and two options
        self.poll = TopicPollFactory.create(topic=self.topic)
        self.option_1 = TopicPollOptionFactory.create(poll=self.poll)
        self.option_2 = TopicPollOptionFactory.create(poll=self.poll)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_vote_in_polls', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_poll_vote', kwargs={'pk': self.poll.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browed_by_users_who_cannot_vote_in_polls(self):
        # Setup
        remove_perm('can_vote_in_polls', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_poll_vote', kwargs={'pk': self.poll.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_can_be_used_to_vote(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_poll_vote', kwargs={'pk': self.poll.pk})
        post_data = {
            'options': [self.option_1.pk, ],
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.status_code == 200
        votes = TopicPollVote.objects.filter(voter=self.user)
        assert votes.count() == 1
        assert votes[0].poll_option == self.option_1

    def test_can_be_used_to_change_a_vote(self):
        # Setup
        self.poll.user_changes = True
        self.poll.save()
        TopicPollVoteFactory.create(voter=self.user, poll_option=self.option_2)
        correct_url = reverse('forum_conversation:topic_poll_vote', kwargs={'pk': self.poll.pk})
        post_data = {
            'options': [self.option_1.pk, ],
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.status_code == 200
        votes = TopicPollVote.objects.filter(voter=self.user)
        assert votes.count() == 1
        assert votes[0].poll_option == self.option_1
