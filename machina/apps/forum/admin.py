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
from guardian.admin import GuardedModelAdmin
from mptt.exceptions import InvalidMove

# Local application / specific library imports
Forum = get_model('forum', 'Forum')


class ForumAdmin(GuardedModelAdmin):
    """
    The ForumAdmin class is a subclass of GuardedModelAdmin and so provides common tools for
    assigning user permissions or group permissions to any forums.
    This class also provides a specific view for moving up or down any forums.
    """
    fieldsets = (
        [None, {
            'fields': ('type', 'parent', 'name', 'description', 'image',)
        }],
        [_('Forum settings'), {
            'fields': ('display_on_index', 'display_sub_forum_list',),
            'classes': ('collapse',)
        }],
        [_('Link forum settings'), {
            'fields': ('link', 'link_redirects',),
            'classes': ('collapse',)
        }],
    )
    list_display = ('name', 'type', 'topics_count', 'posts_count',)
    search_fields = ('name',)
    # Permissions specific attributes
    obj_perms_manage_template = 'admin/forum/forum/obj_perms_manage.html'

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
        self.message_user(request, _("'{}' forum successfully moved").format(forum.name))
        return HttpResponseRedirect(reverse('admin:forum_forum_changelist'))


admin.site.register(Forum, ForumAdmin)
