# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.models.fields import MarkupTextField
from machina.models.fields import MarkupTextFieldWidget

ForumProfile = get_model('forum_member', 'ForumProfile')


class ForumProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'posts_count', )
    list_filter = ('posts_count', )
    list_display_links = ('id', 'user', )
    raw_id_fields = ('user', )
    search_fields = ('user__username',)

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }


admin.site.register(ForumProfile, ForumProfileAdmin)
