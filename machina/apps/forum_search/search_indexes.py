# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from haystack import indexes

from machina.core.db.models import get_model


Post = get_model('forum_conversation', 'Post')


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Defines the data stored in the Post indexes.
    """
    text = indexes.CharField(
        document=True, use_template=True, template_name='forum_search/post_text.txt')

    poster = indexes.IntegerField(model_attr='poster_id', null=True)
    poster_name = indexes.CharField()

    forum = indexes.IntegerField(model_attr='topic__forum_id')
    forum_slug = indexes.CharField()
    forum_name = indexes.CharField()

    topic = indexes.IntegerField(model_attr='topic_id')
    topic_slug = indexes.CharField()
    topic_subject = indexes.CharField()

    created = indexes.DateTimeField(model_attr='created')
    updated = indexes.DateTimeField(model_attr='updated')

    def get_model(self):
        return Post

    def prepare_poster_name(self, obj):
        return obj.poster.username if obj.poster else obj.username

    def prepare_forum_slug(self, obj):
        return obj.topic.forum.slug

    def prepare_forum_name(self, obj):
        return obj.topic.forum.name

    def prepare_topic_slug(self, obj):
        return obj.topic.slug

    def prepare_topic_subject(self, obj):
        return obj.topic.subject

    def index_queryset(self, using=None):
        return Post.objects.all().exclude(approved=False)

    def read_queryset(self, using=None):
        return Post.objects.all().exclude(approved=False).select_related('topic', 'poster')
