# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import View

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.core.loading import get_classes
from machina.views.mixins import PermissionRequiredMixin

Forum = get_model('forum', 'Forum')
ForumReadTrack, TopicReadTrack = get_classes('tracking.models',
                                             ['ForumReadTrack', 'TopicReadTrack'])
Topic = get_model('conversation', 'Topic')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()

TrackingHandler = get_class('tracking.handler', 'TrackingHandler')
track_handler = TrackingHandler()


class MarkForumsReadView(View):
    success_message = _('Forums have been marked read.')

    def get(self, request, pk=None):
        top_level_forum = None

        if pk is not None:
            top_level_forum = get_object_or_404(Forum, pk=pk)
            forums = perm_handler.forum_list_filter(
                top_level_forum.get_descendants(include_self=True), request.user)
            redirect_to = reverse('forum:forum', kwargs={'slug': top_level_forum.slug, 'pk': pk})
        else:
            forums = perm_handler.forum_list_filter(
                Forum.objects.all(), request.user)
            redirect_to = reverse('forum:index')

        # Update all forum tracks to the current date for the considered forums
        for forum in forums:
            forum_track = ForumReadTrack.objects.get_or_create(forum=forum, user=request.user)[0]
            forum_track.save()

        # Delete all the unnecessary topic tracks
        TopicReadTrack.objects.filter(topic__forum__in=forums, user=request.user).delete()

        if len(forums):
            messages.success(request, self.success_message)

        return HttpResponseRedirect(redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkForumsReadView, self).dispatch(request, *args, **kwargs)


class MarkTopicsReadView(PermissionRequiredMixin, View):
    success_message = _('Topics have been marked read.')
    permission_required = ['can_read_forum', ]

    def get(self, request, pk):
        forum = get_object_or_404(Forum, pk=pk)

        # Update the track related to the considered forum to the current date
        forum_track = ForumReadTrack.objects.get_or_create(forum=forum, user=request.user)[0]
        forum_track.save()
        # Delete all the topic tracks associated with this forum
        TopicReadTrack.objects.filter(topic__forum=forum, user=request.user).delete()

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
    template_name = 'tracking/unread_topic_list.html'
    context_object_name = 'topics'
    paginate_by = machina_settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forums = perm_handler.forum_list_filter(
            Forum.objects.all(), self.request.user)
        topics = Topic.objects.filter(forum__in=forums)
        topics_pk = map(lambda t: t.pk, track_handler.get_unread_topics(topics, self.request.user))
        return Topic.objects.filter(pk__in=topics_pk).order_by('-updated')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UnreadTopicsView, self).dispatch(request, *args, **kwargs)
