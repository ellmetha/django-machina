# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class ForumPermissionAdmin(admin.ModelAdmin):
    search_fields = ('codename', )
    list_display = ('name', 'codename', 'is_global', 'is_local', )
    list_editables = ('is_global', 'is_local', )


class GroupForumPermissionAdmin(admin.ModelAdmin):
    search_fields = ('permission__codename', 'group__name', )
    list_display = ('group', 'forum', 'permission', 'has_perm', )
    list_editables = ('has_perm', )
    raw_id_fields = ('group', )


class UserForumPermissionAdmin(admin.ModelAdmin):
    search_fields = ('permission__codename', 'user__username', )
    list_display = ('user', 'anonymous_user', 'forum', 'permission', 'has_perm', )
    list_editables = ('has_perm', )
    raw_id_fields = ('user', )


admin.site.register(ForumPermission, ForumPermissionAdmin)
admin.site.register(GroupForumPermission, GroupForumPermissionAdmin)
admin.site.register(UserForumPermission, UserForumPermissionAdmin)
