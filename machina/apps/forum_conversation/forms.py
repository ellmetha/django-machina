# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class


Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')
TopicPoll = get_model('forum_polls', 'TopicPoll')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')

get_anonymous_user_forum_key = get_class(
    'forum_permission.shortcuts', 'get_anonymous_user_forum_key')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'content', 'username', 'update_reason', 'enable_signature', ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_ip = kwargs.pop('user_ip', None)
        self.forum = kwargs.pop('forum', None)
        self.topic = kwargs.pop('topic', None)

        self.perm_handler = PermissionHandler()

        super(PostForm, self).__init__(*args, **kwargs)

        # Updates the 'subject' and 'content' fields attributes
        self.fields['subject'].widget.attrs['placeholder'] = _('Enter your subject')
        self.fields['content'].label = _('Message')
        self.fields['content'].widget.attrs['placeholder'] = _('Enter your message')

        # Handles anonymous users
        if self.user and self.user.is_anonymous:
            self.fields['username'].required = True
        else:
            # The 'username' field is not really usefull if the user is
            # authenticated
            del self.fields['username']

        # Handles the definition of a default subject if we are
        # considering an answer
        if not self.instance.pk and self.topic:
            self.fields['subject'].initial = '{} {}'.format(
                machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX,
                self.topic.subject)

        # Delete the 'update_reason' field if we are
        # considering a post update
        if not self.instance.pk:
            del self.fields['update_reason']

        # Inserts a field to allow the user to lock the current topic if he has the permissions to
        # do so.
        if (self.instance.pk or self.topic) \
                and self.perm_handler.can_lock_topics(self.forum, self.user):
            self.fields['lock_topic'] = forms.BooleanField(
                label=_('Lock topic'), required=False,
                initial=self.topic.status == Topic.TOPIC_LOCKED)

    def clean(self):
        if not self.instance.pk:
            # Only set user on post creation
            if not self.user.is_anonymous:
                self.instance.poster = self.user
            else:
                self.instance.anonymous_key = get_anonymous_user_forum_key(self.user)
        return super(PostForm, self).clean()

    def save(self, commit=True):
        if self.instance.pk:
            # First handle updates
            post = super(PostForm, self).save(commit=False)
            post.updated_by = self.user
            post.updates_count = F('updates_count') + 1
        else:
            post = Post(
                topic=self.topic,
                poster_ip=self.user_ip,
                subject=self.cleaned_data['subject'],
                approved=self.perm_handler.can_post_without_approval(self.forum, self.user),
                content=self.cleaned_data['content'],
                enable_signature=self.cleaned_data['enable_signature'])
            if not self.user.is_anonymous:
                post.poster = self.user
            else:
                post.username = self.cleaned_data['username']
                post.anonymous_key = get_anonymous_user_forum_key(self.user)

        # Locks the topic if appropriate.
        lock_topic = self.cleaned_data.get('lock_topic', False)
        if lock_topic:
            self.topic.status = Topic.TOPIC_LOCKED
            self.topic.save()

        if commit:
            post.save()

        return post


class TopicForm(PostForm):
    topic_type = forms.ChoiceField(
        label=_('Post topic as'), choices=Topic.TYPE_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)

        # Perform some checks before doing anything
        self.can_add_stickies = self.perm_handler.can_add_stickies(self.forum, self.user)
        self.can_add_announcements = self.perm_handler.can_add_announcements(self.forum, self.user)
        self.can_create_polls = self.perm_handler.can_create_polls(self.forum, self.user)

        if not self.can_add_stickies:
            choices = filter(
                lambda t: t[0] != Topic.TOPIC_STICKY,
                self.fields['topic_type'].choices)
            self.fields['topic_type'].choices = choices
        if not self.can_add_announcements:
            choices = filter(
                lambda t: t[0] != Topic.TOPIC_ANNOUNCE,
                self.fields['topic_type'].choices)
            self.fields['topic_type'].choices = choices

        # Append polls fields to the form if the user is allowed to create such things
        if self.can_create_polls:
            self.fields['poll_question'] = forms.CharField(
                label=_('Poll question'), required=False,
                help_text=_('Enter a question to associate a poll with the topic or leave blank to '
                            'not create a poll.'),
                max_length=TopicPoll._meta.get_field('question').max_length)
            self.fields['poll_max_options'] = forms.IntegerField(
                label=_('Maximum number of poll options per user'), required=False,
                help_text=_('This is the number of options each user may select when voting.'),
                validators=TopicPoll._meta.get_field('max_options').validators,
                initial=TopicPoll._meta.get_field('max_options').default)
            self.fields['poll_duration'] = forms.IntegerField(
                label=_('For how many days the poll should be run?'), required=False,
                help_text=_('Enter 0 or leave blank for a never ending poll.'),
                min_value=0, initial=0)
            self.fields['poll_user_changes'] = forms.BooleanField(
                label=_('Allow re-voting?'), required=False,
                help_text=_('If enabled users are able to change their vote.'),
                initial=False)

        # Set the initial values
        try:
            if hasattr(self.instance, 'topic'):
                self.fields['topic_type'].initial = self.instance.topic.type

                if self.can_create_polls and self.instance.topic.poll is not None:
                    self.fields['poll_question'].initial = self.instance.topic.poll.question
                    self.fields['poll_max_options'].initial = self.instance.topic.poll.max_options
                    self.fields['poll_duration'].initial = self.instance.topic.poll.duration
                    self.fields['poll_user_changes'].initial = self.instance.topic.poll.user_changes
        except ObjectDoesNotExist:
            pass

    def clean(self):
        if self.cleaned_data.get('poll_question', None) \
                and not self.cleaned_data.get('poll_max_options', None):
            self.add_error(
                'poll_max_options',
                _('You must set the maximum number of poll options per user when creating polls'))

        super(TopicForm, self).clean()

    def save(self, commit=True):
        if not self.instance.pk:
            # First, handle topic creation
            if 'topic_type' in self.cleaned_data and len(self.cleaned_data['topic_type']):
                topic_type = self.cleaned_data['topic_type']
            else:
                topic_type = Topic.TOPIC_POST

            topic = Topic(
                forum=self.forum,
                subject=self.cleaned_data['subject'],  # The topic's name is the post's name
                type=topic_type,
                status=Topic.TOPIC_UNLOCKED,
                approved=self.perm_handler.can_post_without_approval(self.forum, self.user))
            if not self.user.is_anonymous:
                topic.poster = self.user
            self.topic = topic
            if commit:
                topic.save()
        else:
            if 'topic_type' in self.cleaned_data and len(self.cleaned_data['topic_type']):
                if self.instance.topic.type != self.cleaned_data['topic_type']:
                    self.instance.topic.type = self.cleaned_data['topic_type']
                    self.instance.topic._simple_save()

        return super(TopicForm, self).save(commit)
