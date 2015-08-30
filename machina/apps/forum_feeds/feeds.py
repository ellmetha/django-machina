# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class LastTopicsFeed(Feed):
    """
    Provides feed items for the latest forum topics.
    """
    # Standard RSS elements
    title = _('Latest topics')
    description = _('Latest topics updated on the forums')
    link = reverse_lazy('forum:index')

    # Item elements
    title_template = 'forum_feeds/topics_title.html'
    description_template = 'forum_feeds/topics_description.html'

    def get_object(self, request, *args, **kwargs):
        forum_pk = kwargs.get('forum_pk', None)
        descendants = kwargs.get('descendants', None)
        self.user = request.user

        if forum_pk:
            forum = get_object_or_404(Forum, pk=forum_pk)
            forums_qs = forum.get_descendants(include_self=True) if descendants \
                else Forum.objects.filter(pk=forum_pk)
            self.forums = perm_handler.forum_list_filter(
                forums_qs, request.user)
        else:
            self.forums = perm_handler.forum_list_filter(
                Forum.objects.all(), request.user)

    def items(self):
        return Topic.objects.filter(forum__in=self.forums, approved=True).order_by('-last_post_on')

    def item_pubdate(self, item):
        return item.created
