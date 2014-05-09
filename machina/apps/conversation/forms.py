# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.loading import get_class

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')
TopicPoll = get_model('polls', 'TopicPoll')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'content', ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_ip = kwargs.pop('user_ip', None)
        self.forum = kwargs.pop('forum', None)
        self.topic = kwargs.pop('topic', None)

        super(PostForm, self).__init__(*args, **kwargs)

        # Updates the 'subject' and 'content' fields attributes
        self.fields['subject'].widget.attrs['placeholder'] = _('Enter your subject')
        self.fields['content'].label = _('Message')
        self.fields['content'].widget.attrs['placeholder'] = _('Enter your message')

        # Handles the definition of a default subject if we are
        # considering an answer
        if not self.instance.pk and self.topic:
            self.fields['subject'].initial = '{} {}'.format(
                machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX,
                self.topic.subject)

    def save(self, commit=True):
        if self.instance.pk:
            # First handle updates
            post = super(PostForm, self).save(commit=False)
            post.updated_by = self.user
            post.updates_count = F('updates_count') + 1
        else:
            post = Post(
                topic=self.topic,
                poster=self.user,
                poster_ip=self.user_ip,
                subject=self.cleaned_data['subject'],
                approved=perm_handler.can_post_without_approval(self.forum, self.user),
                content=self.cleaned_data['content'])

        if commit:
            post.save()

        return post


class TopicForm(PostForm):
    topic_type = forms.ChoiceField(label=_('Post topic as'), choices=Topic.TYPE_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)

        # Perform some checks before doing anything
        self.can_add_stickies = perm_handler.can_add_stickies(self.forum, self.user)
        self.can_add_announcements = perm_handler.can_add_announcements(self.forum, self.user)
        self.can_create_polls = perm_handler.can_create_polls(self.forum, self.user)

        if not self.can_add_stickies:
            choices = filter(
                lambda t: t[0] != Topic.TYPE_CHOICES.topic_sticky,
                self.fields['topic_type'].choices)
            self.fields['topic_type'].choices = choices
        if not self.can_add_announcements:
            choices = filter(
                lambda t: t[0] != Topic.TYPE_CHOICES.topic_announce,
                self.fields['topic_type'].choices)
            self.fields['topic_type'].choices = choices

        # Append polls fields to the form if the user is allowed to create such things
        if self.can_create_polls:
            self.fields['poll_question'] = forms.CharField(
                label=_('Poll question'), required=False,
                max_length=TopicPoll._meta.get_field('question').max_length)
            self.fields['poll_max_options'] = forms.IntegerField(
                label=_('Maximum number of poll options per user'), required=False,
                help_text=_('This is the number of options each user may select when voting.'),
                initial=1)
            self.fields['poll_duration'] = forms.IntegerField(
                label=_('For how many days the poll should be run?'), required=False,
                help_text=_('Enter 0 or leave blank for a never ending poll.'),
                initial=0)

        # Set the initial value for the topic type
        try:
            if hasattr(self.instance, 'topic'):
                self.fields['topic_type'].initial = self.instance.topic.type
        except ObjectDoesNotExist:
            pass

    def save(self, commit=True):
        if not self.instance.pk:
             # First, handle topic creation
            if 'topic_type' in self.cleaned_data and len(self.cleaned_data['topic_type']):
                topic_type = self.cleaned_data['topic_type']
            else:
                topic_type = Topic.TYPE_CHOICES.topic_post

            topic = Topic(
                forum=self.forum,
                poster=self.user,
                subject=self.cleaned_data['subject'],  # The topic's name is the post's name
                type=topic_type,
                status=Topic.STATUS_CHOICES.topic_unlocked)
            self.topic = topic
            if commit:
                topic.save()
        else:
            if 'topic_type' in self.cleaned_data and len(self.cleaned_data['topic_type']):
                if self.instance.topic.type != self.cleaned_data['topic_type']:
                    self.instance.topic.type = self.cleaned_data['topic_type']
                    self.instance.topic._simple_save()

        return super(TopicForm, self).save(commit)
