"""
    Forum feeds
    ===========

    This module defines the feed abstractions provided by the forum application. It allows to
    generate RSS feeds.

"""

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from machina.core.db.models import get_model


Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')


class LastTopicsFeed(Feed):
    """ Provides feed items for the latest forum topics. """

    # Standard RSS elements
    title = _('Latest topics')
    description = _('Latest topics updated on the forums')
    link = reverse_lazy('forum:index')

    # Item elements
    title_template = 'forum_feeds/topics_title.html'
    description_template = 'forum_feeds/topics_description.html'

    def get_object(self, request, *args, **kwargs):
        """ Handles the considered object. """
        forum_pk = kwargs.get('forum_pk', None)
        descendants = kwargs.get('descendants', None)
        self.user = request.user

        if forum_pk:
            forum = get_object_or_404(Forum, pk=forum_pk)
            forums_qs = (
                forum.get_descendants(include_self=True)
                if descendants else Forum.objects.filter(pk=forum_pk)
            )
            self.forums = request.forum_permission_handler.get_readable_forums(
                forums_qs, request.user,
            )
        else:
            self.forums = request.forum_permission_handler.get_readable_forums(
                Forum.objects.all(), request.user,
            )

    def items(self):
        """ Returns the items to include into the feed. """
        return Topic.objects.filter(forum__in=self.forums, approved=True).order_by('-last_post_on')

    def item_link(self, item):
        """ Generates a link for a specific item of the feed. """
        return reverse_lazy(
            'forum_conversation:topic',
            kwargs={
                'forum_slug': item.forum.slug,
                'forum_pk': item.forum.pk,
                'slug': item.slug,
                'pk': item.id,
            },
        )

    def item_pubdate(self, item):
        """ Returns the item's creation date or update date. """
        return item.created
