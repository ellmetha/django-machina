"""
    Forum member model admin definitions
    ====================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin

from machina.core.db.models import get_model
from machina.models.fields import MarkupTextField, MarkupTextFieldWidget


ForumProfile = get_model('forum_member', 'ForumProfile')


class ForumProfileAdmin(admin.ModelAdmin):
    """ The Forum Profile model admin. """

    list_display = ('id', 'user', 'posts_count', )
    list_filter = ('posts_count', )
    list_display_links = ('id', 'user', )
    raw_id_fields = ('user', )
    search_fields = ('user__username',)

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }


admin.site.register(ForumProfile, ForumProfileAdmin)
