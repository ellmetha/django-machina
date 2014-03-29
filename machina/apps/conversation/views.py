# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from django.views.generic import ListView

# Local application / specific library imports
from machina.apps.conversation.signals import topic_viewed
from machina.conf import settings as machina_settings
from machina.core.loading import get_class
from machina.views.mixins import PermissionRequiredMixin

Forum = get_model('forum', 'Forum')
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')

PostForm = get_class('conversation.forms', 'PostForm')
TopicForm = get_class('conversation.forms', 'TopicForm')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class TopicView(PermissionRequiredMixin, ListView):
    template_name = 'conversation/topic_detail.html'
    context_object_name = 'posts'
    permission_required = ['can_read_forum', ]
    paginate_by = machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE
    view_signal = topic_viewed

    def get(self, request, **kwargs):
        topic = self.get_topic()
        response = super(TopicView, self).get(request, **kwargs)
        self.send_signal(request, response, topic)
        return response

    def get_topic(self):
        if not hasattr(self, 'topic'):
            self.topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        return self.topic

    def get_queryset(self):
        self.topic = self.get_topic()
        qs = self.topic.posts.all()
        return qs

    def get_controlled_object(self):
        """
        Returns the forum associated with the current topic in order to allow permission checks.
        """
        return self.get_topic().forum

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)

        # Insert the considered topic and the associated forum into the context
        topic = self.get_topic()
        context['topic'] = topic
        context['forum'] = topic.forum

        return context

    def send_signal(self, request, response, topic):
        self.view_signal.send(
            sender=self, topic=topic, user=request.user,
            request=request, response=response)


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'conversation/topic_create.html'
    permission_required = ['can_start_new_topics', ]

    def get_form_class(self):
        new_topic = 'pk' not in self.kwargs
        if new_topic:
            return TopicForm
        return PostForm

    def get_controlled_object(self):
        """
        Returns the forum associated with the post being created.
        """
        forum_pk = self.kwargs['forum_pk']
        return Forum.objects.get(pk=forum_pk)

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)

        # Insert the considered forum into the context
        forum_pk = self.kwargs['forum_pk']
        context['forum'] = Forum.objects.get(pk=forum_pk)

        return context
