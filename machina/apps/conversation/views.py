# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from django.views.generic import ListView

# Local application / specific library imports
from machina.apps.conversation.signals import topic_viewed
from machina.apps.conversation.utils import get_client_ip
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

        # Handle pagination
        requested_post = request.GET.get('post', None)
        if requested_post:
            try:
                post = topic.posts.get(pk=requested_post)
                requested_page = (post.position // machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE) + 1
                request.GET = request.GET.copy()  # A QueryDict is immutable
                request.GET.update({'page': requested_page})
            except Post.DoesNotExist:
                pass

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


class TopicCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'conversation/topic_create.html'
    permission_required = ['can_start_new_topics', ]
    form_class = TopicForm

    def get_form_kwargs(self):
        kwargs = super(TopicCreateView, self).get_form_kwargs()
        kwargs['forum'] = self.get_forum()
        kwargs['poster'] = self.request.user
        kwargs['poster_ip'] = get_client_ip(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TopicCreateView, self).get_context_data(**kwargs)

        # Insert the considered forum into the context
        context['forum'] = self.get_forum()

        if hasattr(self, 'preview'):
            context['preview'] = self.preview

        return context

    def form_valid(self, form):
        if 'preview' in self.request.POST:
            self.preview = True
            return self.render_to_response(self.get_context_data(form=form))
        return super(TopicCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('conversation:topic', kwargs={
            'forum_pk': self.get_forum().pk,
            'pk': self.object.topic.pk})

    def get_controlled_object(self):
        """
        Returns the forum associated with the post being created.
        """
        return self.get_forum()

    def get_forum(self):
        if not hasattr(self, 'forum'):
            self.forum = get_object_or_404(Forum, pk=self.kwargs['forum_pk'])
        return self.forum
