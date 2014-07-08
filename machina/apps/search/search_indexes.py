# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import get_model
from haystack import indexes

# Local application / specific library imports

Post = get_model('conversation', 'Post')


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, template_name='search/post_text.txt')
    poster = indexes.CharField(model_attr='poster')

    created = indexes.DateTimeField(model_attr='created')
    updated = indexes.DateTimeField(model_attr='updated')

    def get_model(self):
        return Post
