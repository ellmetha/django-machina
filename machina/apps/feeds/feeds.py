# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.syndication.views import Feed
from django.db.models import get_model
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class LastTopicsFeed(Feed):
    # Standard RSS elements
    title = _('Latest topics')
    description = _('Latest topics updated on the forums')
    link = reverse_lazy('forum:index')

    # Item elements
    title_template = 'feeds/topics_title.html'
    description_template = 'feeds/topics_description.html'

    def get_object(self, request, *args, **kwargs):
        self.user = request.user
        self.forums = perm_handler.forum_list_filter(
            Forum.objects.all(), request.user)

    def items(self):
        return Topic.objects.filter(forum__in=self.forums).order_by('-updated')

    def item_pubdate(self, item):
        return item.created
