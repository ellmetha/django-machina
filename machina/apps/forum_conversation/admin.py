# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from machina.core.db.models import get_model
from machina.models.fields import MarkupTextField
from machina.models.fields import MarkupTextFieldWidget

Attachment = get_model('forum_attachments', 'Attachment')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class PostAdmin(admin.ModelAdmin):
    inlines = [AttachmentInline, ]
    list_display = ('__str__', 'topic', 'poster', 'updated', 'approved')
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', )
    search_fields = ('content',)
    list_editable = ('approved',)

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }


class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'forum', 'created', 'first_post', 'last_post', 'posts_count', 'approved')
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', 'subscribers', )
    search_fields = ('subject',)
    list_editable = ('approved',)


admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
