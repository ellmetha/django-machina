# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

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


class MarkForumsReadView(TemplateView):
    """ Marks a set of forums as read. """

    success_message = _('Forums have been marked read.')
    template_name = 'forum_tracking/mark_forums_read.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkForumsReadView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk=None):
        self.top_level_forum = get_object_or_404(Forum, pk=pk) if pk else None
        return super(MarkForumsReadView, self).get(request, pk)

    def get_context_data(self, **kwargs):
        context = super(MarkForumsReadView, self).get_context_data(**kwargs)
        context['top_level_forum'] = self.top_level_forum
        context['top_level_forum_url'] = self.get_top_level_forum_url()
        return context

    def get_top_level_forum_url(self):
        """ Returns the parent forum from which forums are marked as read. """
        return reverse('forum:index') if self.top_level_forum is None else \
            reverse('forum:forum',
                    kwargs={'slug': self.top_level_forum.slug, 'pk': self.kwargs['pk']})

    def mark_as_read(self, request, pk):
        """ Marks the considered forums as read. """
        if self.top_level_forum is not None:
            forums = request.forum_permission_handler.get_readable_forums(
                self.top_level_forum.get_descendants(include_self=True), request.user)
        else:
            forums = request.forum_permission_handler.get_readable_forums(
                Forum.objects.all(), request.user)

        # Marks forums as read
        track_handler.mark_forums_read(forums, request.user)

        if len(forums):
            messages.success(request, self.success_message)

        return HttpResponseRedirect(self.get_top_level_forum_url())

    def post(self, request, pk=None):
        self.top_level_forum = get_object_or_404(Forum, pk=pk) if pk else None
        return self.mark_as_read(request, pk)


class MarkTopicsReadView(
        PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """ Marks a set of topics as read. """

    model = Forum
    success_message = _('Topics have been marked read.')
    permission_required = ['can_read_forum', ]
    template_name = 'forum_tracking/mark_topics_read.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkTopicsReadView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        self.forum = get_object_or_404(Forum, pk=pk)
        return super(MarkTopicsReadView, self).get(request, pk)

    def get_context_data(self, **kwargs):
        context = super(MarkTopicsReadView, self).get_context_data(**kwargs)
        context['forum_url'] = self.get_forum_url()
        return context

    def get_controlled_object(self):
        """ Return the considered forum in order to allow permission checks. """
        return Forum.objects.get(pk=self.kwargs['pk'])

    def get_forum_url(self):
        """ Returns the url of the forum whose topics will be marked read. """
        return reverse('forum:forum', kwargs={'slug': self.forum.slug, 'pk': self.forum.pk})

    def mark_topics_read(self, request, pk):
        # Marks forum topics as read
        track_handler.mark_forums_read([self.forum, ], request.user)
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.get_forum_url())

    def post(self, request, pk):
        self.forum = get_object_or_404(Forum, pk=pk)
        return self.mark_topics_read(request, pk)


class UnreadTopicsView(ListView):
    """ Displays unread topics for the current user. """

    template_name = 'forum_tracking/unread_topic_list.html'
    context_object_name = 'topics'
    paginate_by = machina_settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forums = self.request.forum_permission_handler.get_readable_forums(
            Forum.objects.all(), self.request.user)
        topics = Topic.objects.filter(forum__in=forums)
        topics_pk = map(lambda t: t.pk, track_handler.get_unread_topics(topics, self.request.user))
        return Topic.approved_objects.filter(pk__in=topics_pk).order_by('-last_post_on')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UnreadTopicsView, self).dispatch(request, *args, **kwargs)
