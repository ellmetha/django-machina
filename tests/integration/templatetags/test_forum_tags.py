import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context
from django.template.base import Template
from django.template.loader import render_to_string
from django.test.client import RequestFactory

from machina.apps.forum_permission.middleware import ForumPermissionMiddleware
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import UserFactory, create_category_forum, create_forum


Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

ForumVisibilityContentTree = get_class('forum.visibility', 'ForumVisibilityContentTree')
PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
assign_perm = get_class('forum_permission.shortcuts', 'assign_perm')


@pytest.mark.django_db
class TestForumListTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.loadstatement = '{% load forum_tags %}'
        self.request_factory = RequestFactory()
        self.user = UserFactory.create()

        # Set up a top-level category
        self.top_level_cat = create_category_forum()

        # Set up some forums
        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)

    def test_can_render_a_list_of_forums_according_to_their_minimum_tree_level(self):
        # Setup
        forums = Forum.objects.all()

        request = self.request_factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        request.user = self.user
        ForumPermissionMiddleware().process_request(request)
        t = Template(self.loadstatement + '{% forum_list forums %}')
        c = Context({'forums': ForumVisibilityContentTree.from_forums(forums), 'request': request})
        expected_out = render_to_string(
            'machina/forum/forum_list.html',
            {
                'forum_contents': ForumVisibilityContentTree.from_forums(forums),
                'user': self.user,
                'root_level': 0,
                'root_level_middle': 1,
                'root_level_sub': 2,
            }
        )
        # Run
        rendered = t.render(c)
        # Check
        assert rendered != ''
        assert rendered == expected_out
