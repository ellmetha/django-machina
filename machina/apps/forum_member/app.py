# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class MemberApp(Application):
    name = 'forum-member'

    user_topics_view = get_class('forum_member.views', 'UserTopicsView')

    def get_urls(self):
        urls = [
            url(_(r'^ego/topics/$'), self.user_topics_view.as_view(), name='user-topics'),
        ]
        return patterns('', *urls)


application = MemberApp()
