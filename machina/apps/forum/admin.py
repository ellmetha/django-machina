# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin
from django.db.models import get_model
from mptt.admin import MPTTModelAdmin

# Local application / specific library imports


Forum = get_model('forum', 'Forum')


class ForumAdmin(MPTTModelAdmin):
    list_display = ('name', 'type', 'topics_count', 'posts_count')


admin.site.register(Forum, ForumAdmin)
