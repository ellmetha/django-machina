"""
    Forum attachments model admin definitions
    =========================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin

from machina.core.db.models import get_model


Attachment = get_model('forum_attachments', 'Attachment')


class AttachmentAdmin(admin.ModelAdmin):
    """ The Attachment model admin. """

    list_display = ('id', 'post', 'comment', 'file', )
    list_display_links = ('id', 'post', 'comment', )
    raw_id_fields = ('post', )


admin.site.register(Attachment, AttachmentAdmin)
