# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from mptt.exceptions import InvalidMove

# Local application / specific library imports
Forum = get_model('forum', 'Forum')


class ForumAdmin(admin.ModelAdmin):
    fieldsets = (
        [None, {
            'fields': ('type', 'parent', 'name', 'description', 'image',)
        }],
        [_('General'), {
            'fields': ('display_on_index', 'display_sub_forum_list',)
        }]
    )
    list_display = ('name', 'type', 'topics_count', 'posts_count',)
    search_fields = ('name',)

    def get_urls(self):
        urls = super(ForumAdmin, self).get_urls()
        forum_admin_urls = patterns(
            '',
            url(r'^(?P<forum_id>[0-9]+)/move-forum/(?P<direction>up|down)/$', self.admin_site.admin_view(self.moveforum_view),
                name='forum_forum_move')
        )
        return forum_admin_urls + urls

    def moveforum_view(self, request, forum_id, direction):
        """
        Moves the given forum toward the requested direction.
        """
        forum = get_object_or_404(Forum, pk=forum_id)

        # Fetch the target
        target, position = None, None
        if direction == 'up':
            target, position = forum.get_previous_sibling(), 'left'
        elif direction == 'down':
            target, position = forum.get_next_sibling(), 'right'

        # Do the move
        try:
            assert target is not None
            forum.move_to(target, position)
        except (InvalidMove, AssertionError):
            pass
        self.message_user(request, _("{} successfully moved").format(forum.name))
        return HttpResponseRedirect(reverse('admin:forum_forum_changelist'))


# class ForumAdmin(MPTTModelAdmin):
#     list_display = ('name', 'type', 'topics_count', 'posts_count')


admin.site.register(Forum, ForumAdmin)
