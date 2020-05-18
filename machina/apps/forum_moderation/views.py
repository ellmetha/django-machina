"""
    Forum moderation views
    ======================

    This module defines views provided by the ``forum_moderation`` application.

"""

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.detail import (
    BaseDetailView, SingleObjectMixin, SingleObjectTemplateResponseMixin
)
from django.views.generic.edit import FormMixin, ProcessFormView

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')

TopicMoveForm = get_class('forum_moderation.forms', 'TopicMoveForm')

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


class TopicLockView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """ Provides the ability to lock forum topics. """

    context_object_name = 'topic'
    model = Topic
    success_message = _('This topic has been locked successfully.')
    template_name = 'forum_moderation/topic_lock.html'

    def lock(self, request, *args, **kwargs):
        """ Locks the considered topic and retirects the user to the success URL. """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = Topic.TOPIC_LOCKED
        self.object.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        return self.lock(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        context['forum'] = topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse(
            'forum_conversation:topic',
            kwargs={
                'forum_slug': self.object.forum.slug,
                'forum_pk': self.object.forum.pk,
                'slug': self.object.slug,
                'pk': self.object.pk,
            },
        )

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permission check. """
        return self.request.forum_permission_handler.can_lock_topics(obj, user)


class TopicUnlockView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """ Provides the ability to unlock forum topics. """

    context_object_name = 'topic'
    model = Topic
    template_name = 'forum_moderation/topic_unlock.html'
    success_message = _('This topic has been unlocked successfully.')

    def unlock(self, request, *args, **kwargs):
        """ Unlocks the considered topic and retirects the user to the success URL. """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = Topic.TOPIC_UNLOCKED
        self.object.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        return self.unlock(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        context['forum'] = topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse(
            'forum_conversation:topic',
            kwargs={
                'forum_slug': self.object.forum.slug,
                'forum_pk': self.object.forum.pk,
                'slug': self.object.slug,
                'pk': self.object.pk,
            },
        )

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_lock_topics(obj, user)


class TopicDeleteView(PermissionRequiredMixin, DeleteView):
    """ Provides the ability to delete forum topics. """

    context_object_name = 'topic'
    model = Topic
    success_message = _('This topic has been deleted successfully.')
    template_name = 'forum_moderation/topic_delete.html'

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        context['forum'] = topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        messages.success(self.request, self.success_message)
        return reverse(
            'forum:forum', kwargs={'slug': self.object.forum.slug, 'pk': self.object.forum.pk},
        )

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_delete_topics(obj, user)


class TopicMoveView(
    PermissionRequiredMixin, SingleObjectTemplateResponseMixin, FormMixin, SingleObjectMixin,
    ProcessFormView,
):
    """ Provides the ability to move forum topics. """

    context_object_name = 'topic'
    form_class = TopicMoveForm
    model = Topic
    success_message = _('This topic has been moved successfully.')
    template_name = 'forum_moderation/topic_move.html'

    def get(self, request, *args, **kwargs):
        """ Handles GET requests. """
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        topic = self.get_object()
        context['forum'] = topic.forum
        return context

    def get_form_kwargs(self):
        """ Returns the keyword arguments used to initialize the associated form. """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'topic': self.object,
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        """ Handles a valid form. """
        # Move the topic
        topic = self.object
        new_forum = form.cleaned_data['forum']
        topic.forum = new_forum

        # Eventually lock the topic
        if form.cleaned_data['lock_topic']:
            topic.status = Topic.TOPIC_LOCKED
        else:
            topic.status = Topic.TOPIC_MOVED

        topic.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse(
            'forum_conversation:topic',
            kwargs={
                'forum_slug': self.object.forum.slug,
                'forum_pk': self.object.forum.pk,
                'slug': self.object.slug,
                'pk': self.object.pk,
            },
        )

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_move_topics(obj, user)


class TopicUpdateTypeBaseView(
    PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView,
):
    """ Provides the ability to change the type of forum topics: normal, sticky topic or announce.
    """

    context_object_name = 'topic'
    model = Topic
    success_message = _('This topic type has been changed successfully.')
    template_name = 'forum_moderation/topic_update_type.html'

    # The following attributes should be defined in subclasses.
    question = ''
    target_type = None

    def update_type(self, request, *args, **kwargs):
        """ Updates the type of the considered topic and retirects the user to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.type = self.target_type
        self.object.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        return self.update_type(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        context['question'] = self.question
        topic = self.get_object()
        context['forum'] = topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse(
            'forum_conversation:topic', kwargs={
                'forum_slug': self.object.forum.slug,
                'forum_pk': self.object.forum.pk,
                'slug': self.object.slug,
                'pk': self.object.pk,
            },
        )

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().forum


class TopicUpdateToNormalTopicView(TopicUpdateTypeBaseView):
    """ Provides the ability to switch a topic to a normal topic. """

    question = _('Would you want to change this topic to a default topic?')
    target_type = Topic.TOPIC_POST

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_update_topics_to_normal_topics(obj, user)


class TopicUpdateToStickyTopicView(TopicUpdateTypeBaseView):
    """ Provides the ability to switch a topic to a sticky topic. """

    question = _('Would you want to change this topic to a sticky topic?')
    target_type = Topic.TOPIC_STICKY

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_update_topics_to_sticky_topics(obj, user)


class TopicUpdateToAnnounceView(TopicUpdateTypeBaseView):
    """ Provides the ability to switch a topic to an announce. """

    question = _('Would you want to change this topic to an announce?')
    target_type = Topic.TOPIC_ANNOUNCE

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_update_topics_to_announces(obj, user)


class ModerationQueueListView(PermissionRequiredMixin, ListView):
    """ Displays the moderation queue. """

    context_object_name = 'posts'
    model = Post
    paginate_by = machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE
    template_name = 'forum_moderation/moderation_queue/list.html'

    def get_queryset(self):
        """ Returns the list of items for this view. """
        forums = self.request.forum_permission_handler.get_moderation_queue_forums(
            self.request.user,
        )
        qs = super().get_queryset()
        qs = qs.filter(topic__forum__in=forums, approved=False)
        return qs.order_by('-created')

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_access_moderation_queue(user)


class ModerationQueueDetailView(PermissionRequiredMixin, DetailView):
    """ Displays the details of an item in the moderation queue. """

    context_object_name = 'post'
    model = Post
    template_name = 'forum_moderation/moderation_queue/detail.html'

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)

        post = self.object
        topic = post.topic

        # Handles the case when a poll is associated to the topic.
        try:
            if hasattr(topic, 'poll') and topic.poll.options.exists():
                poll = topic.poll
                context['poll'] = poll
                context['poll_options'] = poll.options.all()
        except ObjectDoesNotExist:  # pragma: no cover
            pass

        if not post.is_topic_head:
            # Add the topic review
            previous_posts = (
                topic.posts
                .filter(approved=True, created__lte=post.created)
                .select_related('poster', 'updated_by')
                .prefetch_related('attachments', 'poster__forum_profile')
                .order_by('-created')
            )
            previous_posts = previous_posts[:machina_settings.TOPIC_REVIEW_POSTS_NUMBER]
            context['previous_posts'] = previous_posts

        return context

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_approve_posts(obj, user)


class PostApproveView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """ Provides the ability to approve queued forum posts. """

    context_object_name = 'post'
    model = Post
    success_message = _('This post has been approved successfully.')
    template_name = 'forum_moderation/moderation_queue/post_approve.html'

    def approve(self, request, *args, **kwargs):
        """ Approves the considered post and retirects the user to the success URL. """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.approved = True
        self.object.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        return self.approve(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        context['forum'] = self.get_object().topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse('forum_moderation:queue')

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_approve_posts(obj, user)


class PostDisapproveView(
    PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView,
):
    """ Provides the ability to disapprove queued forum posts. """

    context_object_name = 'post'
    model = Post
    success_message = _('This post has been disapproved successfully.')
    template_name = 'forum_moderation/moderation_queue/post_disapprove.html'

    def disapprove(self, request, *args, **kwargs):
        """ Disapproves the considered post and retirects the user to the success URL. """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        return self.disapprove(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Returns the context data to provide to the template. """
        context = super().get_context_data(**kwargs)
        context['forum'] = self.get_object().topic.forum
        return context

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse('forum_moderation:queue')

    def get_controlled_object(self):
        """ Returns the controlled object. """
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_approve_posts(obj, user)
