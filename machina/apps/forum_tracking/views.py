# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import View

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.core.loading import get_classes

Forum = get_model('forum', 'Forum')
ForumReadTrack, TopicReadTrack = get_classes('forum_tracking.models',
                                             ['ForumReadTrack', 'TopicReadTrack'])
Topic = get_model('forum_conversation', 'Topic')

TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')
track_handler = TrackingHandler()

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


class MarkForumsReadView(View):
    """
    Marks a set of forums as read.
    """
    success_message = _('Forums have been marked read.')

    def get(self, request, pk=None):
        top_level_forum = None

        if pk is not None:
            top_level_forum = get_object_or_404(Forum, pk=pk)
            forums = request.forum_permission_handler.forum_list_filter(
                top_level_forum.get_descendants(include_self=True), request.user)
            redirect_to = reverse('forum:forum', kwargs={'slug': top_level_forum.slug, 'pk': pk})
        else:
            forums = request.forum_permission_handler.forum_list_filter(
                Forum.objects.all(), request.user)
            redirect_to = reverse('forum:index')

        # Marks forums as read
        track_handler.mark_forums_read(forums, request.user)

        if len(forums):
            messages.success(request, self.success_message)

        return HttpResponseRedirect(redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkForumsReadView, self).dispatch(request, *args, **kwargs)


class MarkTopicsReadView(PermissionRequiredMixin, View):
    """
    Marks a set of topics as read.
    """
    success_message = _('Topics have been marked read.')
    permission_required = ['can_read_forum', ]

    def get(self, request, pk):
        forum = get_object_or_404(Forum, pk=pk)

        # Marks forum topics as read
        track_handler.mark_forums_read([forum, ], request.user)

        messages.success(request, self.success_message)
        redirect_to = reverse('forum:forum', kwargs={'slug': forum.slug, 'pk': pk})

        return HttpResponseRedirect(redirect_to)

    def get_controlled_object(self):
        """
        Return the considered forum in order to allow permission checks.
        """
        return Forum.objects.get(pk=self.kwargs['pk'])

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkTopicsReadView, self).dispatch(request, *args, **kwargs)


class UnreadTopicsView(ListView):
    """
    Displays unread topics for the current user.
    """
    template_name = 'forum_tracking/unread_topic_list.html'
    context_object_name = 'topics'
    paginate_by = machina_settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forums = self.request.forum_permission_handler.forum_list_filter(
            Forum.objects.all(), self.request.user)
        topics = Topic.objects.filter(forum__in=forums)
        topics_pk = map(lambda t: t.pk, track_handler.get_unread_topics(topics, self.request.user))
        return Topic.approved_objects.filter(pk__in=topics_pk).order_by('-last_post_on')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UnreadTopicsView, self).dispatch(request, *args, **kwargs)
