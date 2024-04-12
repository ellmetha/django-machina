"""
    Forum member model admin definitions
    ====================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin
from django.contrib.auth import get_user_model

from machina.core.db.models import get_model
from machina.models.fields import MarkupTextField, MarkupTextFieldWidget

ForumProfile = get_model('forum_member', 'ForumProfile')
USERNAME_FIELD = get_user_model().USERNAME_FIELD


class ForumProfileAdmin(admin.ModelAdmin):
    """ The Forum Profile model admin. """

    list_display = ('id', 'user', 'posts_count',)
    list_filter = ('posts_count',)
    list_display_links = ('id', 'user',)
    raw_id_fields = ('user',)
    search_fields = ('user__%s' % USERNAME_FIELD,)

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }


admin.site.register(ForumProfile, ForumProfileAdmin)
