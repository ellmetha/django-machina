# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from haystack import indexes

# Local application / specific library imports
from machina.core.db.models import get_model

Post = get_model('conversation', 'Post')


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name='search/post_text.txt')

    poster = indexes.CharField(model_attr='poster')
    poster_name = indexes.CharField(model_attr='poster__username')

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
        return obj.topic.poster.username

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
