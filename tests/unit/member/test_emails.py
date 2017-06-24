# -*- coding: utf-8 -*-

import pytest
from django.contrib.sites.models import Site

from machina.apps.forum_member.emails import NotificationEmail
from machina.test.factories import PostFactory
from machina.test.factories import UserFactory
from machina.test.factories import create_forum
from machina.test.factories import create_topic


@pytest.mark.django_db
class TestNotificationEmail(object):
    def test_send_email(self, mailoutbox):
        # Setup
        user = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=user)
        post = PostFactory.create(topic=topic, poster=user)

        email = NotificationEmail(from_email='test@example.com')
        context = {
            'user': user,
            'post': post,
            'topic': post.topic,
            'current_site': Site.objects.get_current(),
        }
        email.send([user.email], context)
        # Send & check
        assert len(mailoutbox) == 1
        notification = mailoutbox[0]
        assert 'New reply on' in notification.subject
        assert 'Hello' in notification.body
        assert '<h2>Hello,</h2>' in notification.alternatives[0][0]
        assert notification.from_email == 'test@example.com'
        assert list(notification.to) == [user.email]
