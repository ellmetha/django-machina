# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

# Local application / specific library imports
from machina.core.loading import get_class
from machina.core.loading import get_classes

Forum = get_model('forum', 'Forum')
ForumReadTrack, TopicReadTrack = get_classes('tracking.models',
                                             ['ForumReadTrack', 'TopicReadTrack'])

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class MarkForumsReadView(View):
    success_message = _('Forums have been marked read.')

    def get(self, request, pk=None):
        top_level_forum = None

        if pk is not None:
            top_level_forum = get_object_or_404(Forum, pk=pk)
            forums = perm_handler.forum_list_filter(
                top_level_forum.get_descendants(include_self=True), request.user)
            redirect_to = reverse('forum:forum', kwargs={'pk': pk})
        else:
            forums = perm_handler.forum_list_filter(
                Forum.objects.all(), request.user)
            redirect_to = reverse('forum:index')

        # Update all forum tracks to the current date for the considered forums.
        for forum in forums:
            forum_track = ForumReadTrack.objects.get_or_create(forum=forum, user=request.user)[0]
            forum_track.save()

        # Delete all the unecessary topic tracks
        TopicReadTrack.objects.filter(topic__forum__in=forums, user=request.user).delete()

        messages.success(request, self.success_message)

        return HttpResponseRedirect(redirect_to)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MarkForumsReadView, self).dispatch(request, *args, **kwargs)
