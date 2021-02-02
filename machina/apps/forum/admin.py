"""
    Forum model admin definitions
    =============================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from collections import OrderedDict

from django.conf.urls import re_path
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.exceptions import InvalidMove

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.models.fields import MarkupTextField, MarkupTextFieldWidget


Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')

PermissionsForm = get_class('forum.forms', 'PermissionsForm')
PickForumForm = get_class('forum.forms', 'PickForumForm')
PickGroupForm = get_class('forum.forms', 'PickGroupForm')
PickUserForm = get_class('forum.forms', 'PickUserForm')

PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


class ForumAdmin(admin.ModelAdmin):
    """ The Forum model admin. """

    formfield_overrides = {
        MarkupTextField: {'widget': MarkupTextFieldWidget},
    }

    fieldsets = (
        [None, {'fields': ('type', 'parent', 'name', 'description', 'image')}],
        [_('Forum settings'), {'fields': ('display_sub_forum_list', ), 'classes': ('collapse', )}],
        [
            _('Link forum settings'),
            {'fields': ('link', 'link_redirects', ), 'classes': ('collapse', )},
        ],
    )
    list_display = ('name', 'type', 'direct_topics_count', 'direct_posts_count', )
    search_fields = ('name', )

    editpermissions_index_view_template_name = 'admin/forum/forum/editpermissions_index.html'
    editpermissions_user_view_template_name = 'admin/forum/forum/editpermissions_user.html'
    editpermissions_anonymous_user_view_template_name = (
        'admin/forum/forum/editpermissions_anonymous_user.html'
    )
    editpermissions_authenticated_user_view_template_name = (
        'admin/forum/forum/editpermissions_authenticated_user.html'
    )
    editpermissions_group_view_template_name = 'admin/forum/forum/editpermissions_group.html'

    def get_urls(self):
        """ Returns the URLs associated with the admin abstraction. """
        urls = super().get_urls()
        forum_admin_urls = [
            re_path(
                r'^(?P<forum_id>[0-9]+)/move-forum/(?P<direction>up|down)/$',
                self.admin_site.admin_view(self.moveforum_view),
                name='forum_forum_move',
            ),
            re_path(
                r'^edit-global-permissions/$',
                self.admin_site.admin_view(self.editpermissions_index_view),
                name='forum_forum_editpermission_index',
            ),
            re_path(
                r'^edit-global-permissions/user/(?P<user_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_user_view),
                name='forum_forum_editpermission_user',
            ),
            re_path(
                r'^edit-global-permissions/user/anonymous/$',
                self.admin_site.admin_view(self.editpermissions_anonymous_user_view),
                name='forum_forum_editpermission_anonymous_user',
            ),
            re_path(
                r'^edit-global-permissions/user/authenticated/$',
                self.admin_site.admin_view(self.editpermissions_authenticated_user_view),
                name='forum_forum_editpermission_authenticated_user',
            ),
            re_path(
                r'^edit-global-permissions/group/(?P<group_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_group_view),
                name='forum_forum_editpermission_group',
            ),
            re_path(
                r'^(?P<forum_id>[0-9]+)/edit-permissions/$',
                self.admin_site.admin_view(self.editpermissions_index_view),
                name='forum_forum_editpermission_index',
            ),
            re_path(
                r'^(?P<forum_id>[0-9]+)/edit-permissions/user/(?P<user_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_user_view),
                name='forum_forum_editpermission_user',
            ),
            re_path(
                r'^(?P<forum_id>[0-9]+)/edit-permissions/user/anonymous/$',
                self.admin_site.admin_view(self.editpermissions_anonymous_user_view),
                name='forum_forum_editpermission_anonymous_user',
            ),
            re_path(
                r'^(?P<forum_id>[0-9]+)/edit-permissions/user/authenticated/$',
                self.admin_site.admin_view(self.editpermissions_authenticated_user_view),
                name='forum_forum_editpermission_authenticated_user',
            ),
            re_path(
                r'^(?P<forum_id>[0-9]+)/edit-permissions/group/(?P<group_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_group_view),
                name='forum_forum_editpermission_group',
            ),
        ]
        return forum_admin_urls + urls

    def get_forum_perms_base_context(self, request, obj=None):
        """ Returns the context to provide to the template for permissions contents. """
        context = {
            'adminform': {'model_admin': self},
            'media': self.media,
            'object': obj,
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, obj),
        }
        try:
            context.update(self.admin_site.each_context(request))
        except TypeError:  # pragma: no cover
            # Django 1.7 compatibility
            context.update(self.admin_site.each_context())
        except AttributeError:  # pragma: no cover
            pass
        return context

    def moveforum_view(self, request, forum_id, direction):
        """ Moves the given forum toward the requested direction. """
        forum = get_object_or_404(Forum, pk=forum_id)

        # Fetch the target
        target, position = None, None
        if direction == 'up':
            target, position = forum.get_previous_sibling(), 'left'
        elif direction == 'down':
            target, position = forum.get_next_sibling(), 'right'

        # Do the move
        try:
            assert target is not None
            forum.move_to(target, position)
        except (InvalidMove, AssertionError):
            pass
        self.message_user(request, _("'{}' forum successfully moved").format(forum.name))
        return HttpResponseRedirect(reverse('admin:forum_forum_changelist'))

    def editpermissions_index_view(self, request, forum_id=None):
        """ Allows to select how to edit forum permissions.

        The view displays a form to select a user or a group in order to edit its permissions for
        the considered forum.

        """
        forum = get_object_or_404(Forum, pk=forum_id) if forum_id \
            else None

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = _('Forum permissions') if forum else _('Global forum permissions')

        can_change_user_perms = (
            request.user.has_perm('forum_permission.add_userforumpermission') or
            request.user.has_perm('forum_permission.change_userforumpermission')
        )
        can_change_group_perms = (
            request.user.has_perm('forum_permission.add_groupforumpermission') or
            request.user.has_perm('forum_permission.change_groupforumpermission')
        )

        # Handles "copy permission from" form
        permissions_copied = False
        if can_change_user_perms and can_change_group_perms:
            if forum and request.method == 'POST':
                forum_form = PickForumForm(request.POST)
                if forum_form.is_valid() and forum_form.cleaned_data['forum']:
                    self._copy_forum_permissions(forum_form.cleaned_data['forum'], forum)
                    self.message_user(request, _('Permissions successfully copied'))
                    permissions_copied = True
                context['forum_form'] = forum_form
            elif forum:
                context['forum_form'] = PickForumForm()

        user_form, user = None, None
        group_form, group = None, None

        # Handles user or group selection
        if request.method == 'POST' and not permissions_copied:
            if can_change_user_perms:
                user_form = PickUserForm(request.POST, admin_site=self.admin_site)
            if can_change_group_perms:
                group_form = PickGroupForm(request.POST, admin_site=self.admin_site)

            # Check if the form was drawn, was valid and was submitted (presence of submitbutton)
            if user_form and user_form.is_valid() and '_select_user' in request.POST:
                user = user_form.cleaned_data.get('user', None) if user_form.cleaned_data else None
                anonymous_user = (
                    user_form.cleaned_data.get('anonymous_user', None)
                    if user_form.cleaned_data else None
                )
                authenticated_user = (
                    user_form.cleaned_data.get('authenticated_user', None)
                    if user_form.cleaned_data else None
                )

                if not user and not anonymous_user and not authenticated_user:
                    user_form._errors[NON_FIELD_ERRORS] = user_form.error_class([
                        _(
                            "Choose either a user ID, the anonymous user or the authenticated user"
                        ),
                    ])
                elif user:
                    # Redirect to user
                    url_kwargs = (
                        {'forum_id': forum.id, 'user_id': user.id}
                        if forum else {'user_id': user.id}
                    )
                    return redirect(
                        reverse('admin:forum_forum_editpermission_user', kwargs=url_kwargs),
                    )
                elif anonymous_user:
                    # Redirect to anonymous user
                    url_kwargs = {'forum_id': forum.id} if forum else {}
                    return redirect(
                        reverse(
                            'admin:forum_forum_editpermission_anonymous_user',
                            kwargs=url_kwargs,
                        ),
                    )
                elif authenticated_user:
                    # Redirect to authenticated user
                    url_kwargs = {'forum_id': forum.id} if forum else {}
                    return redirect(
                        reverse(
                            'admin:forum_forum_editpermission_authenticated_user',
                            kwargs=url_kwargs,
                        ),
                    )

                context['user_errors'] = helpers.AdminErrorList(user_form, [])

            # Check if the form was drawn, was valid and was submitted (presence of submitbutton)
            if group_form and group_form.is_valid() and '_select_group' in request.POST:
                group = group_form.cleaned_data.get('group', None) \
                    if group_form.cleaned_data else None

                if not group:
                    group_form._errors[NON_FIELD_ERRORS] = group_form.error_class(
                        [_('Choose a group ID'), ])
                else:
                    # Redirect to group
                    url_kwargs = (
                        {'forum_id': forum.id, 'group_id': group.id}
                        if forum else {'group_id': group.id}
                    )
                    return redirect(
                        reverse('admin:forum_forum_editpermission_group', kwargs=url_kwargs),
                    )

                context['group_errors'] = helpers.AdminErrorList(group_form, [])
        else:
            if can_change_user_perms:
                user_form = PickUserForm(admin_site=self.admin_site)
            if can_change_group_perms:
                group_form = PickGroupForm(admin_site=self.admin_site)

        context['user_form'] = user_form
        context['group_form'] = group_form

        return render(request, self.editpermissions_index_view_template_name, context)

    def editpermissions_user_view(self, request, user_id, forum_id=None):
        """ Allows to edit user permissions for the considered forum.

        The view displays a form to define which permissions are granted for the given user for the
        considered forum.

        """
        user_model = get_user_model()
        user = get_object_or_404(user_model, pk=user_id)
        forum = get_object_or_404(Forum, pk=forum_id) if forum_id else None

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), user)
        context['form'] = self._get_permissions_form(
            request, UserForumPermission, {'forum': forum, 'user': user},
        )

        return render(request, self.editpermissions_user_view_template_name, context)

    def editpermissions_anonymous_user_view(self, request, forum_id=None):
        """ Allows to edit anonymous user permissions for the considered forum.

        The view displays a form to define which permissions are granted for the anonymous user for
        the considered forum.

        """
        forum = get_object_or_404(Forum, pk=forum_id) if forum_id else None

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), _('Anonymous user'))
        context['form'] = self._get_permissions_form(
            request, UserForumPermission, {'forum': forum, 'anonymous_user': True},
        )

        return render(request, self.editpermissions_anonymous_user_view_template_name, context)

    def editpermissions_authenticated_user_view(self, request, forum_id=None):
        """ Allows to edit authenticated user permissions for the considered forum.

        The view displays a form to define which permissions are granted for the authenticated,
        non-specific, user for the considered forum.

        """
        forum = get_object_or_404(Forum, pk=forum_id) if forum_id else None

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), _('Authenticated user'))
        context['form'] = self._get_permissions_form(
            request, UserForumPermission, {'forum': forum, 'authenticated_user': True},
        )

        return render(request, self.editpermissions_authenticated_user_view_template_name, context)

    def editpermissions_group_view(self, request, group_id, forum_id=None):
        """ Allows to edit group permissions for the considered forum.

        The view displays a form to define which permissions are granted for the given group for the
        considered forum.

        """
        group = get_object_or_404(Group, pk=group_id)
        forum = get_object_or_404(Forum, pk=forum_id) if forum_id else None

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), group)
        context['form'] = self._get_permissions_form(
            request, GroupForumPermission, {'forum': forum, 'group': group},
        )

        return render(request, self.editpermissions_group_view_template_name, context)

    def _get_permissions_form(self, request, permission_model, filter_kwargs):
        # Fetch the permissions
        editable_permissions = sorted(
            ForumPermission.objects.all(), key=lambda p: p.name,
        )
        granted_permissions = (
            permission_model.objects.filter(
                permission__in=editable_permissions, has_perm=True, **filter_kwargs
            )
            .values_list('permission__codename', flat=True)
        )
        non_granted_permissions = (
            permission_model.objects.filter(
                permission__in=editable_permissions, has_perm=False, **filter_kwargs
            )
            .values_list('permission__codename', flat=True)
        )

        permissions_dict = OrderedDict()
        for p in editable_permissions:
            if p.codename in granted_permissions:
                perm_state = PermissionsForm.PERM_GRANTED
            elif p.codename in non_granted_permissions:
                perm_state = PermissionsForm.PERM_NOT_GRANTED
            else:
                perm_state = PermissionsForm.PERM_NOT_SET
            permissions_dict[p.codename] = (p, perm_state)

        if request.method == 'POST':
            form = PermissionsForm(request.POST, permissions_dict=permissions_dict)
            if form.is_valid():
                for codename, value in form.cleaned_data.items():
                    try:
                        perm = permission_model.objects.get(
                            permission=permissions_dict[codename][0], **filter_kwargs
                        )
                    except permission_model.DoesNotExist:
                        if value == PermissionsForm.PERM_NOT_SET:
                            continue
                        perm = permission_model.objects.create(
                            permission=permissions_dict[codename][0], **filter_kwargs
                        )

                    if value == PermissionsForm.PERM_NOT_SET:
                        perm.delete()
                        continue

                    perm.has_perm = (value == PermissionsForm.PERM_GRANTED)
                    perm.save()

                self.message_user(request, _('Permissions successfully applied'))
        else:
            form = PermissionsForm(permissions_dict=permissions_dict)

        return form

    def _copy_forum_permissions(self, forum_from, forum_to):
        user_perms = UserForumPermission.objects.filter(forum=forum_from)
        group_perms = GroupForumPermission.objects.filter(forum=forum_from)

        for perm in user_perms:
            try:
                new_perm = UserForumPermission.objects.get(
                    permission=perm.permission, forum=forum_to,
                    user=perm.user, anonymous_user=perm.anonymous_user,
                )
            except UserForumPermission.DoesNotExist:
                new_perm = UserForumPermission(
                    permission=perm.permission, forum=forum_to,
                    user=perm.user, anonymous_user=perm.anonymous_user,
                    authenticated_user=perm.authenticated_user
                )
            new_perm.has_perm = perm.has_perm
            new_perm.save()

        for perm in group_perms:
            try:
                new_perm = GroupForumPermission.objects.get(
                    permission=perm.permission, forum=forum_to,
                    group=perm.group,
                )
            except GroupForumPermission.DoesNotExist:
                new_perm = GroupForumPermission(
                    permission=perm.permission, forum=forum_to,
                    group=perm.group,
                )
            new_perm.has_perm = perm.has_perm
            new_perm.save()


admin.site.register(Forum, ForumAdmin)
