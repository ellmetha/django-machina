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


class TestTopicView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_triggers_a_viewed_signal(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        # Run & check
        with mock_signal_receiver(topic_viewed) as receiver:
            self.client.get(correct_url, follow=True)
            self.assertEqual(receiver.call_count, 1)

    def test_increases_the_views_counter_of_the_topic(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        initial_views_count = self.topic.views_count
        # Run
        self.client.get(correct_url)
        # Check
        topic = self.topic.__class__._default_manager.get(pk=self.topic.pk)
        self.assertEqual(topic.views_count, initial_views_count + 1)

    def test_cannot_change_the_updated_date_of_the_topic(self):
        # Setup
        correct_url = self.topic.get_absolute_url()
        initial_updated_date = self.topic.updated
        # Run
        self.client.get(correct_url)
        # Check
        topic = self.topic.__class__._default_manager.get(pk=self.topic.pk)
        self.assertEqual(topic.updated, initial_updated_date)

    def test_marks_the_related_forum_as_read_if_no_other_unread_topics_are_present(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        PostFactory.create(topic=new_topic, poster=self.user)
        TopicReadTrackFactory.create(topic=new_topic, user=self.user)
        TopicReadTrackFactory.create(topic=self.topic, user=self.user)
        PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        topic_tracks = TopicReadTrack.objects.all()
        self.assertEqual(forum_tracks.count(), 1)
        self.assertFalse(len(topic_tracks))
        self.assertEqual(forum_tracks[0].forum, self.topic.forum)
        self.assertEqual(forum_tracks[0].user, self.user)

    def test_marks_the_related_topic_as_read_if_other_unread_topics_are_present(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        PostFactory.create(topic=new_topic, poster=self.user)
        PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        topic_tracks = TopicReadTrack.objects.all()
        self.assertEqual(topic_tracks.count(), 1)
        self.assertEqual(topic_tracks[0].topic, self.topic)
        self.assertEqual(topic_tracks[0].user, self.user)

    def test_marks_the_related_topic_as_read_even_if_no_track_is_registered_for_the_related_forum(self):
        # Setup
        top_level_forum_alt = create_forum()
        topic_alt = create_topic(forum=top_level_forum_alt, poster=self.user)
        PostFactory.create(topic=topic_alt, poster=self.user)
        assign_perm('can_read_forum', self.user, top_level_forum_alt)
        correct_url = topic_alt.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.filter(forum=top_level_forum_alt)
        topic_tracks = TopicReadTrack.objects.all()
        self.assertEqual(forum_tracks.count(), 1)
        self.assertEqual(topic_tracks.count(), 0)

    def test_cannot_create_any_track_if_the_user_is_not_authenticated(self):
        # Setup
        ForumReadTrack.objects.all().delete()
        assign_perm('can_read_forum', get_anonymous_user(), self.top_level_forum)
        self.client.logout()
        correct_url = self.topic.get_absolute_url()
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        topic_tracks = TopicReadTrack.objects.all()
        self.assertFalse(len(forum_tracks))
        self.assertFalse(len(topic_tracks))

    def test_can_paginate_based_on_a_post_id(self):
        # Setup
        for _ in range(0, 40):
            # 15 posts per page
            PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run & check
        first_post_pk = self.topic.first_post.pk
        response = self.client.get(correct_url, {'post': first_post_pk}, follow=True)
        self.assertEqual(response.context_data['page_obj'].number, 1)
        mid_post_pk = self.topic.first_post.pk + 18
        response = self.client.get(correct_url, {'post': mid_post_pk}, follow=True)
        self.assertEqual(response.context_data['page_obj'].number, 2)
        last_post_pk = self.topic.last_post.pk
        response = self.client.get(correct_url, {'post': last_post_pk}, follow=True)
        self.assertEqual(response.context_data['page_obj'].number, 3)

    def test_properly_handles_a_bad_post_id_in_parameters(self):
        # Setup
        for _ in range(0, 40):
            # 15 posts per page
            PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = self.topic.get_absolute_url()
        # Run & check
        bad_post_pk = self.topic.first_post.pk + 50000
        response = self.client.get(correct_url, {'post': bad_post_pk}, follow=True)
        self.assertEqual(response.context_data['page_obj'].number, 1)
        response = self.client.get(correct_url, {'post': 'I\'m a post'}, follow=True)
        self.assertEqual(response.context_data['page_obj'].number, 1)

    def test_embed_poll_data_into_the_context_if_a_poll_is_associated_to_the_topic(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        TopicPollOptionFactory.create(poll=poll)
        TopicPollOptionFactory.create(poll=poll)
        correct_url = self.topic.get_absolute_url()
        # Run & check
        response = self.client.get(correct_url)
        self.assertEqual(response.context_data['poll'], poll)
        self.assertTrue(isinstance(response.context_data['poll_form'], TopicPollVoteForm))


class TestTopicCreateView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicCreateView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_embed_the_current_forum_into_the_context(self):
        # Setup
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertEqual(response.context_data['forum'], self.top_level_forum)

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['preview'])

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': response.context_data['topic'].slug, 'pk': response.context_data['topic'].pk})
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(topic_url, last_url)

    def test_embed_a_poll_option_formset_in_the_context_if_the_user_can_create_polls(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        self.assertIn('poll_option_formset', response.context_data)
        self.assertTrue(isinstance(response.context_data['poll_option_formset'], TopicPollOptionFormset))

    def test_cannot_embed_a_poll_option_formset_in_the_context_if_the_user_canot_create_polls(self):
        # Setup
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        self.assertFalse('poll_option_formset' in response.context_data)

    def test_can_handle_poll_previews(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'preview': 'Preview',
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-1-id': '',
            'poll-1-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['poll_preview'])

    def test_can_create_a_poll_and_its_options_if_the_user_is_allowed_to_do_it(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-1-id': '',
            'poll-1-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic = Topic.objects.get(pk=response.context_data['topic'].pk)
        self.assertTrue(topic.poll is not None)
        self.assertEqual(topic.poll.question, post_data['poll_question'])
        self.assertEqual(topic.poll.max_options, post_data['poll_max_options'])
        self.assertEqual(topic.poll.duration, post_data['poll_duration'])
        self.assertEqual(topic.poll.options.count(), 2)
        self.assertEqual(topic.poll.options.all()[0].text, post_data['poll-0-text'])
        self.assertEqual(topic.poll.options.all()[1].text, post_data['poll-1-text'])

    def test_cannot_create_polls_with_invalid_options(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse('conversation:topic-create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data_1 = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 1,
            'poll-MAX_NUM_FORMS': 1000,
        }
        post_data_2 = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-1-id': '',
            'poll-1-text': faker.text(max_nb_chars=100) * 1000,
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        response_1 = self.client.post(correct_url, post_data_1, follow=True)
        response_2 = self.client.post(correct_url, post_data_2, follow=True)
        # Check
        messages_1 = list(response_1.context['messages'])
        self.assertEqual(len(messages_1), 1)
        self.assertEqual(messages_1[0].level, MSG.ERROR)
        messages_2 = list(response_2.context['messages'])
        self.assertEqual(len(messages_2), 1)
        self.assertEqual(messages_2[0].level, MSG.ERROR)


class TestTopicUpdateView(BaseClientTestCase):
    def setUp(self):
        super(TestTopicUpdateView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_embed_the_current_forum_into_the_context(self):
        # Setup
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertEqual(response.context_data['forum'], self.top_level_forum)

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['preview'])

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(topic_url, last_url)

    def test_embed_a_poll_option_formset_in_the_context_if_the_user_can_add_polls(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        self.assertIn('poll_option_formset', response.context_data)
        self.assertTrue(isinstance(response.context_data['poll_option_formset'], TopicPollOptionFormset))

    def test_cannot_embed_a_poll_option_formset_in_the_context_if_the_user_canot_add_polls(self):
        # Setup
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        self.assertFalse('poll_option_formset' in response.context_data)

    def test_can_handle_poll_previews(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'preview': 'Preview',
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-1-id': '',
            'poll-1-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['poll_preview'])

    def test_allows_poll_updates(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'poll_question': faker.text(max_nb_chars=155),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': option_1.pk,
            'poll-0-text': option_1.text,
            'poll-1-id': option_2.pk,
            'poll-1-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 2,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        option_2 = refresh(option_2)
        self.assertEqual(option_2.text, post_data['poll-1-text'])
        poll = refresh(poll)
        self.assertEqual(poll.question, post_data['poll_question'])

    def test_allows_poll_creations(self):
        # Setup
        assign_perm('can_create_poll', self.user, self.top_level_forum)
        correct_url = reverse(
            'conversation:topic-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': TOPIC_TYPES.topic_post,
            'poll_question': faker.text(max_nb_chars=100),
            'poll_max_options': 1,
            'poll_duration': 0,
            'poll-0-id': '',
            'poll-0-text': faker.text(max_nb_chars=100),
            'poll-1-id': '',
            'poll-1-text': faker.text(max_nb_chars=100),
            'poll-INITIAL_FORMS': 0,
            'poll-TOTAL_FORMS': 2,
            'poll-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic = Topic.objects.get(pk=response.context_data['topic'].pk)
        self.assertTrue(topic.poll is not None)
        self.assertEqual(topic.poll.question, post_data['poll_question'])
        self.assertEqual(topic.poll.max_options, post_data['poll_max_options'])
        self.assertEqual(topic.poll.duration, post_data['poll_duration'])
        self.assertEqual(topic.poll.options.count(), 2)
        self.assertEqual(topic.poll.options.all()[0].text, post_data['poll-0-text'])
        self.assertEqual(topic.poll.options.all()[1].text, post_data['poll-1-text'])


class TestPostCreateView(BaseClientTestCase):
    def setUp(self):
        super(TestPostCreateView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'conversation:post-create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_embed_the_current_topic_into_the_context(self):
        # Setup
        correct_url = reverse(
            'conversation:post-create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertEqual(response.context_data['topic'], self.topic)

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'conversation:post-create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['preview'])

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'conversation:post-create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'conversation:topic',
            kwargs={
                'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                'slug': response.context_data['topic'].slug, 'pk': response.context_data['topic'].pk})
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(topic_url, last_url)


class TestPostUpdateView(BaseClientTestCase):
    def setUp(self):
        super(TestPostUpdateView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'conversation:post-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_embed_the_current_topic_into_the_context(self):
        # Setup
        correct_url = reverse(
            'conversation:post-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertEqual(response.context_data['topic'], self.topic)

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'conversation:post-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        self.assertTrue(response.context_data['preview'])

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'conversation:post-update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(topic_url, last_url)


class TestPostDeleteView(BaseClientTestCase):
    def setUp(self):
        super(TestPostDeleteView, self).setUp()

        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'conversation:post-delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        self.assertIsOk(response)

    def test_redirects_to_the_topic_view_if_posts_remain(self):
        # Setup
        correct_url = reverse(
            'conversation:post-delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(topic_url, last_url)

    def test_redirects_to_the_forum_view_if_no_posts_remain(self):
        # Setup
        self.post.delete()
        correct_url = reverse(
            'conversation:post-delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        forum_url = reverse(
            'forum:forum',
            kwargs={'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.pk, })
        self.assertGreater(len(response.redirect_chain), 0)
        last_url, status_code = response.redirect_chain[-1]
        self.assertIn(forum_url, last_url)
