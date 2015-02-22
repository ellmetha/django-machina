# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin

# Local application / specific library imports
from machina.core.db.models import get_model

Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'comment', 'file', )
    list_display_links = ('id', 'post', 'comment', )
    raw_id_fields = ('post', )


admin.site.register(Attachment, AttachmentAdmin)
