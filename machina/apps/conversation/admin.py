# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin
from django.db.models import get_model

# Local application / specific library imports
Post = get_model('conversation', 'Post')
Topic = get_model('conversation', 'Topic')


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


class PostAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'topic', 'poster', 'updated',)
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', )
    search_fields = ('content',)


class TopicAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('subject', 'forum', 'created', 'first_post', 'last_post', 'posts_count',)
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', 'subscribers', )
    search_fields = ('subject',)


admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
