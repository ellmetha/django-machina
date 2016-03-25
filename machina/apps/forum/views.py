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

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


class IndexView(ListView):
    """
    Displays the top-level forums.
    """
    template_name = 'forum/index.html'
    context_object_name = 'forums'

    def get_queryset(self):
        return self.request.forum_permission_handler.forum_list_filter(
            Forum.objects.displayable_subforums(),
            self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        top_level_forums = context['forums'].filter(parent__isnull=True)
        context['total_posts_count'] = sum(f.posts_count for f in top_level_forums)
        context['total_topics_count'] = sum(f.topics_count for f in top_level_forums)

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
            .select_related('poster')
        return qs

    def get_controlled_object(self):
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super(ForumView, self).get_context_data(**kwargs)

        # Insert the considered forum into the context
        context['forum'] = self.get_forum()

        # Get the list of forums that have the current forum as parent
        sub_forums = Forum.objects.displayable_subforums(start_from=self.forum)
        context['sub_forums'] = self.request.forum_permission_handler \
            .forum_list_filter(sub_forums, self.request.user)

        # The announces will be displayed on each page of the forum
        context['announces'] = self.get_forum().topics.filter(type=Topic.TOPIC_ANNOUNCE)

        return context

    def send_signal(self, request, response, forum):
        self.view_signal.send(
            sender=self, forum=forum, user=request.user,
            request=request, response=response)
