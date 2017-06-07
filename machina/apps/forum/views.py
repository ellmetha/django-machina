# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from machina.apps.forum.signals import forum_viewed
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')
Topic = get_model('forum_conversation', 'Topic')

ForumVisibilityContentTree = get_class('forum.visibility', 'ForumVisibilityContentTree')
PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')
TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')


class IndexView(ListView):
    """
    Displays the top-level forums.
    """
    template_name = 'forum/index.html'
    context_object_name = 'forums'

    def get_queryset(self):
        return ForumVisibilityContentTree.from_forums(
            self.request.forum_permission_handler.forum_list_filter(
                Forum.objects.all(), self.request.user))

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        visiblity_content_tree = context['forums']

        # Computes some global values.
        context['total_posts_count'] = sum(n.posts_count for n in visiblity_content_tree.top_nodes)
        context['total_topics_count'] = sum(
            n.topics_count for n in visiblity_content_tree.top_nodes)

        return context


class ForumView(PermissionRequiredMixin, ListView):
    """
    Displays a forums and its topics. If applicable, its sub-forums can
    also be displayed.
    """
    template_name = 'forum/forum_detail.html'
    context_object_name = 'topics'
    permission_required = ['can_read_forum', ]
    paginate_by = machina_settings.FORUM_TOPICS_NUMBER_PER_PAGE
    view_signal = forum_viewed

    def get(self, request, **kwargs):
        forum = self.get_forum()
        if forum.is_link:
            response = HttpResponseRedirect(forum.link)
        else:
            response = super(ForumView, self).get(request, **kwargs)
        self.send_signal(request, response, forum)
        return response

    def get_forum(self):
        """
        Returns the forum to consider.
        """
        if not hasattr(self, 'forum'):
            self.forum = get_object_or_404(Forum, pk=self.kwargs['pk'])
        return self.forum

    def get_queryset(self):
        self.forum = self.get_forum()
        qs = self.forum.topics.exclude(type=Topic.TOPIC_ANNOUNCE).exclude(approved=False) \
            .select_related('poster', 'last_post', 'last_post__poster')
        return qs

    def get_controlled_object(self):
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super(ForumView, self).get_context_data(**kwargs)

        # Insert the considered forum into the context
        context['forum'] = self.get_forum()

        # Get the list of forums that have the current forum as parent
        context['sub_forums'] = ForumVisibilityContentTree.from_forums(
            self.request.forum_permission_handler.forum_list_filter(
                context['forum'].get_descendants(), self.request.user))

        # The announces will be displayed on each page of the forum
        context['announces'] = list(
            self.get_forum().topics.select_related('poster', 'last_post', 'last_post__poster')
            .filter(type=Topic.TOPIC_ANNOUNCE))

        # Determines the topics that have not been read by the current user
        context['unread_topics'] = TrackingHandler(self.request).get_unread_topics(
            list(context[self.context_object_name]) + context['announces'], self.request.user)

        return context

    def send_signal(self, request, response, forum):
        self.view_signal.send(
            sender=self, forum=forum, user=request.user,
            request=request, response=response)
