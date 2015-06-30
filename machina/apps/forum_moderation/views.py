# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import get_class

Topic = get_model('forum_conversation', 'Topic')

PermissionRequiredMixin = get_class('forum_permission.mixins', 'PermissionRequiredMixin')


class TopicCloseView(PermissionRequiredMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    A view providing the ability to close forum topics.
    """
    template_name = 'forum_moderation/topic_close.html'
    context_object_name = 'topic'
    success_message = _('This topic has been closed successfully.')
    model = Topic

    def close(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status = Topic.STATUS_CHOICES.topic_locked
        self.object.save()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.close(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TopicCloseView, self).get_context_data(**kwargs)

        # Append the topic and the forum associated with the post being deleted
        # to the context
        topic = self.get_object()
        context['forum'] = topic.forum

        return context

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse('forum-conversation:topic', kwargs={
            'forum_slug': self.object.forum.slug,
            'forum_pk': self.object.forum.pk,
            'slug': self.object.slug,
            'pk': self.object.pk})

    # Permissions checks

    def get_controlled_object(self):
        """
        Returns the post that will be edited.
        """
        return self.get_object().forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_close_topics(obj, user)
