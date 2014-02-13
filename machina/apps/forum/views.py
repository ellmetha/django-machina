# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

# Local application / specific library imports
from machina.apps.forum.signals import forum_viewed
from machina.conf import settings as machina_settings
from machina.core.loading import get_class
from machina.views.mixins import PermissionRequiredMixin

Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class IndexView(ListView):
    template_name = 'forum/index.html'
    context_object_name = 'forums'

    def get_queryset(self):
        return perm_handler.forum_list_filter(
            Forum.objects.filter(
                # Forums that have a top-level category has parent
                Q(parent__parent__isnull=True, parent__type=Forum.TYPE_CHOICES.forum_cat) |
                # Sub forums that can be displayed
                Q(parent__parent__isnull=True, display_sub_forum_list=True) |
                # Children of forums that have a category as parent
                Q(parent__parent__parent__isnull=True,
                    parent__parent__type=Forum.TYPE_CHOICES.forum_cat,
                    parent__type=Forum.TYPE_CHOICES.forum_post,
                    display_sub_forum_list=True) |
                # Category, top-level forums and links
                Q(parent__isnull=True)),
            self.request.user
        )


class ForumView(PermissionRequiredMixin, ListView):
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
        if not hasattr(self, 'forum'):
            self.forum = get_object_or_404(Forum, pk=self.kwargs['pk'])
        return self.forum

    def get_queryset(self):
        self.forum = self.get_forum()
        qs = self.forum.topics.all()
        return qs

    def get_controlled_object(self):
        """
        Return the considered forum in order to allow permission checks.
        """
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super(ForumView, self).get_context_data(**kwargs)

        # Insert the considered forum into the context
        context['forum'] = self.get_forum()

        # Get the list of forums that have the current forum as parent
        sub_forums = Forum.objects.filter(
            # Forums that have a top-level category has parent
            Q(parent__parent__pk=self.forum.pk, parent__type=Forum.TYPE_CHOICES.forum_cat) |
            # Sub forums that can be displayed
            Q(parent__parent__pk=self.forum.pk, display_sub_forum_list=True) |
            # Children of forums that have a category as parent
            Q(parent__parent__parent=self.forum,
                parent__parent__type=Forum.TYPE_CHOICES.forum_cat,
                parent__type=Forum.TYPE_CHOICES.forum_post,
                display_sub_forum_list=True) |
            # Category, top-level forums and links
            Q(parent=self.forum))

        context['sub_forums'] = perm_handler.forum_list_filter(sub_forums, self.request.user)

        return context

    def send_signal(self, request, response, forum):
        self.view_signal.send(
            sender=self, forum=forum, user=request.user,
            request=request, response=response)
