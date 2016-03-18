# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView
from django.views.generic.edit import ModelFormMixin

from machina.core.db.models import get_model
from machina.core.loading import get_class

TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')

TopicPollVoteForm = get_class('forum_polls.forms', 'TopicPollVoteForm')

PermissionRequiredMixin = get_class('forum_permission.viewmixins', 'PermissionRequiredMixin')


class TopicPollVoteView(PermissionRequiredMixin, UpdateView):
    """
    Allows to vote in polls.
    """
    model = TopicPoll
    form_class = TopicPollVoteForm
    http_method_names = ['post', ]

    def get_form_kwargs(self):
        kwargs = super(ModelFormMixin, self).get_form_kwargs()
        kwargs['poll'] = self.object
        return kwargs

    def form_valid(self, form):
        user_kwargs = {'voter': self.request.user} if self.request.user.is_authenticated() \
            else {'anonymous_key': self.request.user.forum_key}

        if self.object.user_changes:
            # If user changes are allowed for this poll, all
            # the poll associated with the current user must
            # be deleted.
            TopicPollVote.objects.filter(
                poll_option__poll=self.object,
                **user_kwargs).delete()

        options = form.cleaned_data['options']
        for option in options:
            TopicPollVote.objects.create(
                poll_option=option, **user_kwargs)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors[NON_FIELD_ERRORS])
        return redirect(reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.topic.forum.slug,
            'forum_pk': self.object.topic.forum.pk,
            'slug': self.object.topic.slug,
            'pk': self.object.topic.pk}))

    def get_success_url(self):
        messages.success(self.request, _('Your vote has been cast.'))
        return reverse('forum_conversation:topic', kwargs={
            'forum_slug': self.object.topic.forum.slug,
            'forum_pk': self.object.topic.forum.pk,
            'slug': self.object.topic.slug,
            'pk': self.object.topic.pk})

    # Permissions checks

    def get_controlled_object(self):
        return self.get_object()

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_vote_in_poll(obj, user)
