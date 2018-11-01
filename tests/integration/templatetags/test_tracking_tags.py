import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context
from django.template.base import Template
from django.test.client import RequestFactory

from machina.apps.forum_permission.middleware import ForumPermissionMiddleware
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import (
    ForumReadTrackFactory, GroupFactory, PostFactory, TopicReadTrackFactory, UserFactory,
    create_category_forum, create_forum, create_topic
)


Forum = get_model('forum', 'Forum')

assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')

TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')


@pytest.mark.django_db
class BaseTrackingTagsTestCase(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.loadstatement = '{% load forum_tracking_tags %}'
        self.request_factory = RequestFactory()

        # Tracking handler
        self.tracks_handler = TrackingHandler()

        self.g1 = GroupFactory.create()
        self.u1 = UserFactory.create()
        self.u2 = UserFactory.create()
        self.u1.groups.add(self.g1)
        self.u2.groups.add(self.g1)

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

        # Set up some topics and posts
        self.forum_1_topic = create_topic(forum=self.forum_1, poster=self.u1)
        self.forum_2_topic = create_topic(forum=self.forum_2, poster=self.u1)
        self.post_1 = PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        self.post_2 = PostFactory.create(topic=self.forum_2_topic, poster=self.u1)

        # Assign some permissions
        assign_perm('can_see_forum', self.g1, self.top_level_cat)
        assign_perm('can_read_forum', self.g1, self.top_level_cat)
        assign_perm('can_see_forum', self.g1, self.forum_1)
        assign_perm('can_read_forum', self.g1, self.forum_1)
        assign_perm('can_see_forum', self.g1, self.forum_2)
        assign_perm('can_read_forum', self.g1, self.forum_2)

    def get_request(self, url='/'):
        request = self.request_factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request


class TestUnreadTopicsTag(BaseTrackingTagsTestCase):
    def test_can_determine_unread_forums(self):
        # Setup
        def get_rendered(topics, user):
            request = self.get_request()
            request.user = user
            ForumPermissionMiddleware().process_request(request)
            t = Template(
                self.loadstatement + '{% get_unread_topics topics request.user as unread_topics %}')
            c = Context({'topics': topics, 'request': request})
            rendered = t.render(c)

            return c, rendered

        # Run & check
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        assert rendered == ''
        assert set(context['unread_topics']) == set(self.forum_2.topics.all())

        # forum_2 topics are now read
        TopicReadTrackFactory.create(topic=self.forum_2_topic, user=self.u2)
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        assert rendered == ''
        assert not len(context['unread_topics'])

        # A new post is created with a pre-existing topic track
        PostFactory.create(topic=self.forum_2_topic, poster=self.u1)
        context, rendered = get_rendered(self.forum_2.topics.all(), self.u2)
        assert rendered == ''
        assert set(context['unread_topics']) == set(self.forum_2.topics.all())

        # A new post is created with a pre-existing forum track
        ForumReadTrackFactory.create(forum=self.forum_1, user=self.u2)
        PostFactory.create(topic=self.forum_1_topic, poster=self.u1)
        context, rendered = get_rendered(self.forum_1.topics.all(), self.u2)
        assert rendered == ''
        assert set(context['unread_topics']) == set(self.forum_1.topics.all())
