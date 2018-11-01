"""
    Forum conversation model admin definitions
    ==========================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin

from machina.core.db.models import get_model
from machina.models.fields import MarkupTextField, MarkupTextFieldWidget


Attachment = get_model('forum_attachments', 'Attachment')
Post = get_model('forum_conversation', 'Post')
Topic = get_model('forum_conversation', 'Topic')


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class PostAdmin(admin.ModelAdmin):
    """ The Post model admin. """

    inlines = [AttachmentInline, ]
    list_display = ('__str__', 'topic', 'poster', 'updated', 'approved')
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', 'topic',)
    search_fields = ('content',)
    list_editable = ('approved',)

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }


class TopicAdmin(admin.ModelAdmin):
    """ The Topic model admin. """

    list_display = (
        'subject', 'forum', 'created', 'first_post', 'last_post', 'posts_count', 'approved',
    )
    list_filter = ('created', 'updated',)
    raw_id_fields = ('poster', 'subscribers', )
    search_fields = ('subject',)
    list_editable = ('approved',)


admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
