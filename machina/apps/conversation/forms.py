# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import forms
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports

Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['subject', 'content', ]

    def __init__(self, *args, **kwargs):
        self.poster = kwargs.pop('poster', None)
        self.poster_ip = kwargs.pop('poster_ip', None)
        self.topic = kwargs.pop('topic', None)
        super(PostForm, self).__init__(*args, **kwargs)


class TopicForm(PostForm):
    topic_type = forms.ChoiceField(label=_('Post topic as'), choices=Topic.TYPE_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        self.forum = kwargs.pop('forum', None)
        super(TopicForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # First, handle updates
        if self.instance.pk:
            pass

        if self.forum and self.topic is None:
            if 'topic_type' in self.cleaned_data:
                topic_type = self.cleaned_data['topic_type']
            else:
                topic_type = Topic.TYPE_CHOICES.topic_post

            topic = Topic(
                forum=self.forum,
                poster=self.poster,
                type=topic_type,
                status=Topic.STATUS_CHOICES.topic_unlocked)
            if commit:
                topic.save()
        else:
            topic = self.topic

        post = Post(
            topic=topic,
            poster=self.poster,
            poster_ip=self.poster_ip,
            subject=self.cleaned_data['subject'],
            content=self.cleaned_data['content'])

        if commit:
            post.save()

        return post
