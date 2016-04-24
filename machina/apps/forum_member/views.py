# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model('forum', 'Forum')
ForumProfile = get_model('forum_member', 'ForumProfile')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

ForumProfileForm = get_class('forum_member.forms', 'ForumProfileForm')

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class UserTopicsView(ListView):
    """
    Provides a list of all the topics in which the current user has
    posted messages.
    """
    template_name = 'forum_member/user_topics_list.html'
    context_object_name = 'topics'
    paginate_by = machina_settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forums = perm_handler.forum_list_filter(
            Forum.objects.all(), self.request.user)
        topics = Topic.objects.filter(
            forum__in=forums,
            posts__poster_id=self.request.user.id,
            posts__approved=True)
        return topics.order_by('-updated')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserTopicsView, self).dispatch(request, *args, **kwargs)


class ForumProfileDetailView(DetailView):
    """
    Shows a user's forum profile.
    """
    template_name = 'forum_member/forum_profile_detail.html'
    context_object_name = 'profile'

    def get_queryset(self):
        user_model = get_user_model()
        return user_model.objects.all()

    def get_object(self, queryset=None):
        user = super(ForumProfileDetailView, self).get_object(queryset)
        profile, dummy = ForumProfile.objects.get_or_create(user=user)
        return profile

    def get_context_data(self, **kwargs):
        context = super(ForumProfileDetailView, self).get_context_data(**kwargs)

        # Computes the number of topics added by the considered member
        context['topics_count'] = Topic.objects.filter(
            approved=True, poster=self.object.user).count()

        # Fetches the recent posts added by the considered user
        forums = self.request.forum_permission_handler.forum_list_filter(
            Forum.objects.all(), self.request.user)
        recent_posts = Post.approved_objects.filter(
            topic__forum__in=forums, poster=self.object.user).order_by('-created')
        context['recent_posts'] = recent_posts[:machina_settings.PROFILE_RECENT_POSTS_NUMBER]

        return context


class ForumProfileUpdateView(UpdateView):
    """
    Allows the current user to update its forum profile.
    """
    template_name = 'forum_member/forum_profile_update.html'
    form_class = ForumProfileForm
    success_message = _('The profile has been edited successfully.')

    def get_object(self, queryset=None):
        profile, dummy = ForumProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        response = super(ForumProfileUpdateView, self).form_valid(form)
        messages.success(self.request, self.success_message)
        return response

    def get_success_url(self):
        return reverse('forum_member:profile_update')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ForumProfileUpdateView, self).dispatch(request, *args, **kwargs)


class TopicSubscribeView(
        PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    Allows a user to subscribe to a specific topic.
    """
    model = Topic
    success_message = _('You subscribed to this topic successfully.')
    template_name = 'forum_member/topic_subscribe.html'

    def subscribe(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.subscribers.add(request.user)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.subscribe(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicSubscribeView, self).get_context_data(**kwargs)
        context['topic'] = self.object
        context['forum'] = self.object.forum
        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug, 'forum_pk': self.object.forum.pk,
            'slug': self.object.slug, 'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TopicSubscribeView, self).dispatch(request, *args, **kwargs)

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_subscribe_to_topic(obj, user)


class TopicUnsubscribeView(
        PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    Allows a user to unsubscribe from a specific topic.
    """
    model = Topic
    success_message = _('You unsubscribed from this topic successfully.')
    template_name = 'forum_member/topic_unsubscribe.html'

    def unsubscribe(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.subscribers.remove(request.user)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        return self.unsubscribe(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicUnsubscribeView, self).get_context_data(**kwargs)
        context['topic'] = self.object
        context['forum'] = self.object.forum
        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug, 'forum_pk': self.object.forum.pk,
            'slug': self.object.slug, 'pk': self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TopicUnsubscribeView, self).dispatch(request, *args, **kwargs)

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_unsubscribe_from_topic(obj, user)
