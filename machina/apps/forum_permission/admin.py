"""
    Forum permission model admin definitions
    ========================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin

from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class ForumPermissionAdmin(admin.ModelAdmin):
    """ The Forum Permission model admin. """

    search_fields = ('codename', )
    list_display = ('name', 'codename', )


class GroupForumPermissionAdmin(admin.ModelAdmin):
    """ The Group Forum Permission model admin. """

    search_fields = ('permission__codename', 'group__name', )
    list_display = ('group', 'forum', 'permission', 'has_perm', )
    list_editables = ('has_perm', )
    raw_id_fields = ('group', )
    list_filter = ['forum', 'group']


class UserForumPermissionAdmin(admin.ModelAdmin):
    """ The User Forum Permission model admin. """

    search_fields = ('permission__codename', 'user__username', )
    list_display = (
        'user',
        'anonymous_user',
        'authenticated_user',
        'forum',
        'permission',
        'has_perm',
    )
    list_editables = ('has_perm', )
    raw_id_fields = ('user', )
    list_filter = ['forum']


admin.site.register(ForumPermission, ForumPermissionAdmin)
admin.site.register(GroupForumPermission, GroupForumPermissionAdmin)
admin.site.register(UserForumPermission, UserForumPermissionAdmin)
