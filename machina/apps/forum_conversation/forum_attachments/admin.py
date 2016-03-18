# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from machina.core.db.models import get_model

Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'comment', 'file', )
    list_display_links = ('id', 'post', 'comment', )
    raw_id_fields = ('post', )


admin.site.register(Attachment, AttachmentAdmin)
