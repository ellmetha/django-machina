# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url

# Local application / specific library imports
from machina.core.app import Application
from machina.core.loading import get_class


class PollsApp(Application):
    name = None

    attachment_view = get_class('forum_conversation.forum_attachments.views', 'AttachmentView')

    def get_urls(self):
        urls = [
            url(r'^attachment/(?P<pk>\d+)/$', self.attachment_view.as_view(), name='attachment'),
        ]
        return patterns('', *urls)


application = PollsApp()
