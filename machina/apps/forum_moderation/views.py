# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.views.generic.edit import ProcessFormView

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

TopicMoveForm = get_class('forum_moderation.forms', 'TopicMoveForm')

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


class TopicLockView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to lock forum topics.
    """
    template_name = 'forum_moderation/topic_lock.html'
    context_object_name = 'topic'
    success_message = _('This topic has been locked successfully.')
    model = Topic

    def lock(self, request, *args, **kwargs):
        """
        Locks the considered topic and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = Topic.TOPIC_LOCKED
        self.object.save()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.lock(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicLockView, self).get_context_data(**kwargs)

        # Append the forum associated with the topic being locked
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug,
            'forum_pk': self.object.forum.pk,
            'slug': self.object.slug,
            'pk': self.object.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_lock_topics(obj, user)


class TopicUnlockView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to unlock forum topics.
    """
    template_name = 'forum_moderation/topic_unlock.html'
    context_object_name = 'topic'
    success_message = _('This topic has been unlocked successfully.')
    model = Topic

    def unlock(self, request, *args, **kwargs):
        """
        Unlocks the considered topic and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = Topic.TOPIC_UNLOCKED
        self.object.save()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.unlock(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicUnlockView, self).get_context_data(**kwargs)

        # Append the forum associated with the topic being locked
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug,
            'forum_pk': self.object.forum.pk,
            'slug': self.object.slug,
            'pk': self.object.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_lock_topics(obj, user)


class TopicDeleteView(PermissionRequiredMixin, DeleteView):
    """
    A view providing the ability to delete forum topics.
    """
    template_name = 'forum_moderation/topic_delete.html'
    context_object_name = 'topic'
    success_message = _('This topic has been deleted successfully.')
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicDeleteView, self).get_context_data(**kwargs)

        # Append the forum associated with the topic being deleted
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def delete(self, request, *args, **kwargs):
        """
        Deletes the considered topic and retirects the user to the success URL.
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        This is a workaround for versions of Django prior 1.6
        where the get_success_url() method was called after
        the delete() method.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse('forum:forum', kwargs={
            'slug': self.object.forum.slug,
            'pk': self.object.forum.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_delete_topics(obj, user)


class TopicMoveView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin,
                    FormMixin, SingleObjectMixin, ProcessFormView):
    """
    A view providing the ability to move forum topics.
    """
    template_name = 'forum_moderation/topic_move.html'
    form_class = TopicMoveForm
    context_object_name = 'topic'
    success_message = _('This topic has been moved successfully.')
    model = Topic

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(TopicMoveView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(TopicMoveView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicMoveView, self).get_context_data(**kwargs)

        # Append the forum associated with the topic being deleted
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def get_form_kwargs(self):
        kwargs = super(TopicMoveView, self).get_form_kwargs()
        kwargs.update({
            'topic': self.object,
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        # Move the topic
        topic = self.object
        old_forum = topic.forum
        new_forum = form.cleaned_data['forum']
        topic.forum = new_forum

        # Eventually lock the topic
        if form.cleaned_data['lock_topic']:
            topic.status = Topic.TOPIC_LOCKED
        else:
            topic.status = Topic.TOPIC_MOVED

        topic.save()
        old_forum.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug,
            'forum_pk': self.object.forum.pk,
            'slug': self.object.slug,
            'pk': self.object.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_move_topics(obj, user)


class TopicUpdateTypeBaseView(
        PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to change the type of forum topics: normal, sticky topic or
    announce.
    """
    template_name = 'forum_moderation/topic_update_type.html'
    context_object_name = 'topic'
    model = Topic
    success_message = _('This topic type has been changed successfully.')

    # The following attributes should be defined in subclasses
    target_type = None
    question = ''

    def update_type(self, request, *args, **kwargs):
        """
        Updates the type of the considered topic and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.type = self.target_type
        self.object.save()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.update_type(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicUpdateTypeBaseView, self).get_context_data(**kwargs)
        context['question'] = self.question

        # Append the forum associated with the topic being locked
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug,
            'forum_pk': self.object.forum.pk,
            'slug': self.object.slug,
            'pk': self.object.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().forum


class TopicUpdateToNormalTopicView(TopicUpdateTypeBaseView):
    target_type = Topic.TOPIC_POST
    question = _('Would you want to change this topic to a default topic?')

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_update_topics_to_normal_topics(obj, user)


class TopicUpdateToStickyTopicView(TopicUpdateTypeBaseView):
    target_type = Topic.TOPIC_STICKY
    question = _('Would you want to change this topic to a sticky topic?')

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_update_topics_to_sticky_topics(obj, user)


class TopicUpdateToAnnounceView(TopicUpdateTypeBaseView):
    target_type = Topic.TOPIC_ANNOUNCE
    question = _('Would you want to change this topic to an announce?')

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_update_topics_to_announces(obj, user)


class ModerationQueueListView(PermissionRequiredMixin, ListView):
    template_name = 'forum_moderation/moderation_queue/list.html'
    context_object_name = 'posts'
    paginate_by = machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE
    model = Post

    def get_queryset(self):
        forums = self.request.forum_permission_handler.get_moderation_queue_forums(
            self.request.user)
        qs = super(ModerationQueueListView, self).get_queryset()
        qs = qs.filter(topic__forum__in=forums, approved=False)
        return qs.order_by('-created')

    # Permissions checks

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_access_moderation_queue(user)


class ModerationQueueDetailView(PermissionRequiredMixin, DetailView):
    template_name = 'forum_moderation/moderation_queue/detail.html'
    context_object_name = 'post'
    model = Post

    def get_context_data(self, **kwargs):
        context = super(ModerationQueueDetailView, self).get_context_data(**kwargs)

        post = self.object
        topic = post.topic

        # Handles the case when a poll is associated to the topic
        try:
            if hasattr(topic, 'poll') and topic.poll.options.exists():
                poll = topic.poll
                context['poll'] = poll
                context['poll_options'] = poll.options.all()
        except ObjectDoesNotExist:  # pragma: no cover
            pass

        if not post.is_topic_head:
            # Add the topic review
            previous_posts = topic.posts.filter(approved=True, created__lte=post.created) \
                .select_related('poster', 'updated_by') \
                .prefetch_related('attachments', 'poster__forum_profile') \
                .order_by('-created')
            previous_posts = previous_posts[:machina_settings.TOPIC_REVIEW_POSTS_NUMBER]
            context['previous_posts'] = previous_posts

        return context

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_approve_posts(obj, user)


class PostApproveView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to approve queued forum posts.
    """
    template_name = 'forum_moderation/moderation_queue/post_approve.html'
    context_object_name = 'post'
    success_message = _('This post has been approved successfully.')
    model = Post

    def approve(self, request, *args, **kwargs):
        """
        Approves the considered post and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.approved = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.approve(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostApproveView, self).get_context_data(**kwargs)
        context['forum'] = self.get_object().topic.forum
        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('forum_moderation:queue')

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_approve_posts(obj, user)


class PostDisapproveView(
        PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to disapprove queued forum posts.
    """
    template_name = 'forum_moderation/moderation_queue/post_disapprove.html'
    context_object_name = 'post'
    success_message = _('This post has been disapproved successfully.')
    model = Post

    def disapprove(self, request, *args, **kwargs):
        """
        Disapproves the considered post and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.disapprove(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PostDisapproveView, self).get_context_data(**kwargs)
        context['forum'] = self.get_object().topic.forum
        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('forum_moderation:queue')

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_approve_posts(obj, user)
