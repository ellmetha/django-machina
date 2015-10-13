# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from machina.apps.forum_conversation.views import TopicView as BaseTopicView

# Local application / specific library imports


class TopicView(BaseTopicView):
    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        # Some additional data can be added to the context here
        context['foo'] = 'bar'
        return context
