# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import constants as MSG  # noqa
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from faker import Factory as FakerFactory
import pytest

from machina.apps.forum_conversation.forum_attachments.forms import AttachmentFormset
from machina.apps.forum_conversation.forum_polls.forms import TopicPollOptionFormset
from machina.apps.forum_conversation.forum_polls.forms import TopicPollVoteForm
from machina.apps.forum_conversation.signals import topic_viewed
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.context_managers import mock_signal_receiver
from machina.test.factories import AttachmentFactory
from machina.test.factories import create_forum
from machina.test.factories import create_topic
from machina.test.factories import ForumReadTrackFactory
from machina.test.factories import PostFactory
from machina.test.factories import TopicPollFactory
from machina.test.factories import TopicPollOptionFactory
from machina.test.factories import TopicReadTrackFactory
from machina.test.testcases import BaseClientTestCase

faker = FakerFactory.create()

ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')
remove_perm = get_class('forum_permission.shortcuts', 'remove_perm')


class TestTopicView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_triggers_a_viewed_signal(self):
        # Setup
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run & check
        with mock_signal_receiver(topic_viewed) as receiver:
            self.client.get(correct_url, follow=True)
            assert receiver.call_count == 1

    def test_increases_the_views_counter_of_the_topic(self):
        # Setup
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        initial_views_count = self.topic.views_count
        # Run
        self.client.get(correct_url)
        # Check
        topic = self.topic.__class__._default_manager.get(pk=self.topic.pk)
        assert topic.views_count == initial_views_count + 1

    def test_cannot_change_the_updated_date_of_the_topic(self):
        # Setup
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        initial_updated_date = self.topic.updated
        # Run
        self.client.get(correct_url)
        # Check
        topic = self.topic.__class__._default_manager.get(pk=self.topic.pk)
        assert topic.updated == initial_updated_date

    def test_marks_the_related_forum_as_read_if_no_other_unread_topics_are_present(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        PostFactory.create(topic=new_topic, poster=self.user)
        TopicReadTrackFactory.create(topic=new_topic, user=self.user)
        TopicReadTrackFactory.create(topic=self.topic, user=self.user)
        PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        topic_tracks = TopicReadTrack.objects.all()
        assert forum_tracks.count() == 1
        assert not len(topic_tracks)
        assert forum_tracks[0].forum == self.topic.forum
        assert forum_tracks[0].user == self.user

    def test_marks_the_related_topic_as_read_if_other_unread_topics_are_present(self):
        # Setup
        new_topic = create_topic(forum=self.top_level_forum, poster=self.user)
        PostFactory.create(topic=new_topic, poster=self.user)
        PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run
        self.client.get(correct_url)
        # Check
        topic_tracks = TopicReadTrack.objects.all()
        assert topic_tracks.count() == 1
        assert topic_tracks[0].topic == self.topic
        assert topic_tracks[0].user == self.user

    def test_marks_the_related_topic_as_read_even_if_no_track_is_registered_for_the_related_forum(self):  # noqa
        # Setup
        top_level_forum_alt = create_forum()
        topic_alt = create_topic(forum=top_level_forum_alt, poster=self.user)
        PostFactory.create(topic=topic_alt, poster=self.user)
        assign_perm('can_read_forum', self.user, top_level_forum_alt)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': top_level_forum_alt.slug, 'forum_pk': top_level_forum_alt.pk,
            'slug': topic_alt.slug, 'pk': topic_alt.id})
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.filter(forum=top_level_forum_alt)
        topic_tracks = TopicReadTrack.objects.all()
        assert forum_tracks.count() == 1
        assert not topic_tracks.count()

    def test_cannot_create_any_track_if_the_user_is_not_authenticated(self):
        # Setup
        ForumReadTrack.objects.all().delete()
        assign_perm('can_read_forum', AnonymousUser(), self.top_level_forum)
        self.client.logout()
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run
        self.client.get(correct_url)
        # Check
        forum_tracks = ForumReadTrack.objects.all()
        topic_tracks = TopicReadTrack.objects.all()
        assert not len(forum_tracks)
        assert not len(topic_tracks)

    def test_can_paginate_based_on_a_post_id(self):
        # Setup
        for _ in range(0, 40):
            # 15 posts per page
            PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run & check
        first_post_pk = self.topic.first_post.pk
        response = self.client.get(correct_url, {'post': first_post_pk}, follow=True)
        assert response.context_data['page_obj'].number == 1
        mid_post_pk = self.topic.first_post.pk + 18
        response = self.client.get(correct_url, {'post': mid_post_pk}, follow=True)
        assert response.context_data['page_obj'].number == 2
        last_post_pk = self.topic.last_post.pk
        response = self.client.get(correct_url, {'post': last_post_pk}, follow=True)
        assert response.context_data['page_obj'].number == 3

    def test_properly_handles_a_bad_post_id_in_parameters(self):
        # Setup
        for _ in range(0, 40):
            # 15 posts per page
            PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run & check
        bad_post_pk = self.topic.first_post.pk + 50000
        response = self.client.get(correct_url, {'post': bad_post_pk}, follow=True)
        assert response.context_data['page_obj'].number == 1
        response = self.client.get(correct_url, {'post': 'I\'m a post'}, follow=True)
        assert response.context_data['page_obj'].number == 1

    def test_embed_poll_data_into_the_context_if_a_poll_is_associated_to_the_topic(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        TopicPollOptionFactory.create(poll=poll)
        TopicPollOptionFactory.create(poll=poll)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run & check
        response = self.client.get(correct_url)
        assert response.context_data['poll'] == poll
        assert isinstance(response.context_data['poll_form'], TopicPollVoteForm)

    def test_cannot_be_browsed_by_users_who_cannot_browse_the_related_forum(self):
        # Setup
        remove_perm('can_read_forum', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
            'slug': self.topic.slug, 'pk': self.topic.id})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403


class TestTopicCreateView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)
        assign_perm('can_post_without_approval', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_start_new_topics(self):
        # Setup
        remove_perm('can_start_new_topics', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_embed_the_current_forum_into_the_context(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.context_data['forum'] == self.top_level_forum

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['preview']

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': response.context_data['topic'].slug,
                    'pk': response.context_data['topic'].pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_redirects_to_the_forum_if_the_post_is_not_approved(self):
        # Setup
        remove_perm('can_post_without_approval', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        forum_url = reverse(
            'forum:forum',
            kwargs={'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert forum_url in last_url

    def test_embed_a_poll_option_formset_in_the_context_if_the_user_can_create_polls(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert 'poll_option_formset' in response.context_data
        assert isinstance(response.context_data['poll_option_formset'], TopicPollOptionFormset)

    def test_cannot_embed_a_poll_option_formset_in_the_context_if_the_user_canot_create_polls(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert response.context_data['poll_option_formset'] is None

    def test_can_handle_poll_previews(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['poll_preview']

    def test_can_create_a_poll_and_its_options_if_the_user_is_allowed_to_do_it(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic = Topic.objects.get(pk=response.context_data['topic'].pk)
        assert topic.poll is not None
        assert topic.poll.question == post_data['poll_question']
        assert topic.poll.max_options == post_data['poll_max_options']
        assert topic.poll.duration == post_data['poll_duration']
        assert topic.poll.options.count() == 2
        assert post_data['poll-0-text'] in topic.poll.options.values_list('text', flat=True)
        assert post_data['poll-1-text'] in topic.poll.options.values_list('text', flat=True)

    def test_cannot_create_polls_with_invalid_options(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data_1 = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        response_1 = self.client.post(correct_url, post_data_1, follow=True)
        response_2 = self.client.post(correct_url, post_data_2, follow=True)
        # Check
        messages_1 = list(response_1.context['messages'])
        assert len(messages_1) >= 1
        assert all(m.level == MSG.ERROR for m in messages_1)
        messages_2 = list(response_2.context['messages'])
        assert len(messages_2) >= 1
        assert all(m.level == MSG.ERROR for m in messages_2)

    def test_embed_an_attachment_formset_in_the_context_if_the_user_can_create_attachments(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert 'attachment_formset' in response.context_data
        assert isinstance(response.context_data['attachment_formset'], AttachmentFormset)

    def test_cannot_embed_an_attachment_formset_in_the_context_if_the_user_canot_create_attachments(self):  # noqa
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert response.context_data['attachment_formset'] is None

    def test_can_handle_attachment_previews(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
            'attachment-0-id': '',
            'attachment-0-file': f,
            'attachment-0-comment': '',
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 2,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['attachment_preview']

    def test_can_handle_multiple_attachment_previews_and_the_persistence_of_the_uploaded_files(self):  # noqa
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        post_data_1 = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
            'attachment-0-id': '',
            'attachment-0-file': f,
            'attachment-0-comment': '',
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 1,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        post_data_2 = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
            'attachment-0-id': '',
            'attachment-0-file': '',
            'attachment-0-comment': '',
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 1,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        response_1 = self.client.post(correct_url, post_data_1, follow=True)
        response_2 = self.client.post(correct_url, post_data_2, follow=True)
        # Check
        assert response_1.context_data['attachment_preview']
        assert response_2.context_data['attachment_preview']
        assert len(response_2.context_data['attachment_file_previews']) == 1
        assert response_2.context_data['attachment_file_previews'][0][1] == 'file1.txt'

    def test_can_create_an_attachment_and_its_options_if_the_user_is_allowed_to_do_it(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'attachment-0-id': '',
            'attachment-0-file': f,
            'attachment-0-comment': '',
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 2,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        post = Topic.objects.get(pk=response.context_data['topic'].pk).first_post
        assert post.attachments.exists()
        assert post.attachments.count() == 1

    def test_cannot_create_attachments_with_invalid_options(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'attachment-0-id': '',
            'attachment-0-file': f,
            'attachment-0-comment': faker.text(max_nb_chars=100) * 1000,
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 2,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert messages[0].level == MSG.ERROR

    def test_cannot_create_topics_with_invalid_data(self):
        # Setup
        correct_url = reverse('forum_conversation:topic_create', kwargs={
            'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '',
            'topic_type': Topic.TOPIC_POST,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.status_code == 200
        assert response.context['post_form'].errors


class TestTopicUpdateView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_start_new_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_edit_their_topics(self):
        # Setup
        remove_perm('can_edit_own_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_embed_the_current_forum_into_the_context(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.context_data['forum'] == self.top_level_forum

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['preview']

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_embed_a_poll_option_formset_in_the_context_if_the_user_can_add_polls(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert 'poll_option_formset' in response.context_data
        assert isinstance(response.context_data['poll_option_formset'], TopicPollOptionFormset)

    def test_cannot_embed_a_poll_option_formset_in_the_context_if_the_user_canot_add_polls(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert response.context_data['poll_option_formset'] is None

    def test_can_handle_poll_previews(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['poll_preview']

    def test_allows_poll_updates(self):
        # Setup
        poll = TopicPollFactory.create(topic=self.topic)
        option_1 = TopicPollOptionFactory.create(poll=poll)
        option_2 = TopicPollOptionFactory.create(poll=poll)
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        option_2.refresh_from_db()
        assert option_2.text == post_data['poll-1-text']
        poll.refresh_from_db()
        assert poll.question == post_data['poll_question']

    def test_allows_poll_creations(self):
        # Setup
        assign_perm('can_create_polls', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
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
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic = Topic.objects.get(pk=response.context_data['topic'].pk)
        assert topic.poll is not None
        assert topic.poll.question == post_data['poll_question']
        assert topic.poll.max_options == post_data['poll_max_options']
        assert topic.poll.duration == post_data['poll_duration']
        assert topic.poll.options.count() == 2
        assert post_data['poll-0-text'] in topic.poll.options.values_list('text', flat=True)
        assert post_data['poll-1-text'] in topic.poll.options.values_list('text', flat=True)

    def test_embed_an_attachment_formset_in_the_context_if_the_user_can_create_attachments(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert 'attachment_formset' in response.context_data
        assert isinstance(response.context_data['attachment_formset'], AttachmentFormset)

    def test_cannot_embed_an_attachment_formset_in_the_context_if_the_user_canot_create_attachments(self):  # noqa
        # Setup
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        assert response.context_data['attachment_formset'] is None

    def test_can_handle_attachment_previews(self):
        # Setup
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'preview': 'Preview',
            'attachment-0-id': '',
            'attachment-0-file': f,
            'attachment-0-comment': '',
            'attachment-INITIAL_FORMS': 0,
            'attachment-TOTAL_FORMS': 1,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['attachment_preview']

    def test_allows_attachment_updates(self):
        # Setup
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        attachment = AttachmentFactory.create(post=self.topic.first_post, file=f)
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'attachment-0-id': attachment.pk,
            'attachment-0-file': attachment.file,
            'attachment-0-comment': 'new comment',
            'attachment-INITIAL_FORMS': 1,
            'attachment-TOTAL_FORMS': 1,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        attachment.refresh_from_db()
        assert attachment.comment == post_data['attachment-0-comment']

    def test_allows_attachment_creations(self):
        # Setup
        f = SimpleUploadedFile('file1.txt', force_bytes('file_content_1'))
        new_file = SimpleUploadedFile('file2.txt', force_bytes('file_content_2'))
        attachment = AttachmentFactory.create(post=self.topic.first_post, file=f)
        assign_perm('can_attach_file', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:topic_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'topic_type': Topic.TOPIC_POST,
            'attachment-0-id': attachment.pk,
            'attachment-0-file': attachment.file,
            'attachment-0-comment': 'new comment',
            'attachment-1-id': '',
            'attachment-1-file': new_file,
            'attachment-1-comment': '',
            'attachment-INITIAL_FORMS': 1,
            'attachment-TOTAL_FORMS': 2,
            'attachment-MAX_NUM_FORMS': 1000,
        }
        # Run
        self.client.post(correct_url, post_data, follow=True)
        # Check
        attachments = self.topic.first_post.attachments
        assert attachments.count() == 2


class TestPostCreateView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_reply_to_topics(self):
        # Setup
        remove_perm('can_reply_to_topics', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_embed_the_current_topic_into_the_context(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.context_data['topic'] == self.topic

    def test_embed_the_topic_review_into_the_context(self):
        # Setup
        p2 = PostFactory.create(topic=self.topic, poster=self.user)
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert 'previous_posts' in response.context_data
        assert set(response.context_data['previous_posts']) == set([p2, self.post, ])

    def test_context_topic_review_contains_only_approved_posts(self):
        # Setup
        p2 = PostFactory.create(topic=self.topic, poster=self.user)
        PostFactory.create(topic=self.topic, poster=self.user, approved=False)
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert 'previous_posts' in response.context_data
        assert set(response.context_data['previous_posts']) == set([p2, self.post, ])

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['preview']

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={
                'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                'slug': response.context_data['topic'].slug,
                'pk': response.context_data['topic'].pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_cannot_create_posts_with_invalid_data(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_create',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk})
        post_data = {
            'subject': '',
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.status_code == 200
        assert response.context['post_form'].errors


class TestPostUpdateView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_edit_their_posts(self):
        # Setup
        remove_perm('can_edit_own_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:post_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_embed_the_current_topic_into_the_context(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.context_data['topic'] == self.topic

    def test_can_detect_that_a_preview_should_be_done(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
            'preview': 'Preview',
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        assert response.context_data['preview']

    def test_redirects_to_topic_view_on_success(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_update',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.post.pk})
        post_data = {
            'subject': faker.text(max_nb_chars=200),
            'content': '[b]{}[/b]'.format(faker.text()),
        }
        # Run
        response = self.client.post(correct_url, post_data, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url


class TestPostDeleteView(BaseClientTestCase):
    @pytest.fixture(autouse=True)
    def setUp(self):
        # Permission handler
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.top_level_forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.top_level_forum, poster=self.user)
        self.first_post = PostFactory.create(topic=self.topic, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Mark the forum as read
        ForumReadTrackFactory.create(forum=self.top_level_forum, user=self.user)

        # Assign some permissions
        assign_perm('can_read_forum', self.user, self.top_level_forum)
        assign_perm('can_reply_to_topics', self.user, self.top_level_forum)
        assign_perm('can_edit_own_posts', self.user, self.top_level_forum)
        assign_perm('can_delete_own_posts', self.user, self.top_level_forum)

    def test_browsing_works(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 200

    def test_cannot_be_browsed_by_users_who_cannot_delete_their_posts(self):
        # Setup
        remove_perm('can_delete_own_posts', self.user, self.top_level_forum)
        correct_url = reverse(
            'forum_conversation:post_delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.get(correct_url, follow=True)
        # Check
        assert response.status_code == 403

    def test_redirects_to_the_topic_view_if_posts_remain(self):
        # Setup
        correct_url = reverse(
            'forum_conversation:post_delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        topic_url = reverse(
            'forum_conversation:topic',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'slug': self.topic.slug, 'pk': self.topic.pk})
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert topic_url in last_url

    def test_redirects_to_the_forum_view_if_no_posts_remain(self):
        # Setup
        self.post.delete()
        correct_url = reverse(
            'forum_conversation:post_delete',
            kwargs={'forum_slug': self.top_level_forum.slug, 'forum_pk': self.top_level_forum.pk,
                    'topic_slug': self.topic.slug, 'topic_pk': self.topic.pk,
                    'pk': self.first_post.pk})
        # Run
        response = self.client.post(correct_url, follow=True)
        # Check
        forum_url = reverse(
            'forum:forum',
            kwargs={'slug': self.top_level_forum.slug, 'pk': self.top_level_forum.pk, })
        assert len(response.redirect_chain)
        last_url, status_code = response.redirect_chain[-1]
        assert forum_url in last_url
