# -*- coding: utf-8 -*-

# Standard library imports
from collections import OrderedDict

# Third party imports
from django import forms
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from mptt.exceptions import InvalidMove

# Local application / specific library imports
from machina.core.compat import get_user_model
from machina.core.db.models import get_model

Forum = get_model('forum', 'Forum')
ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


PERM_GRANTED = 'granted'
PERM_NOT_GRANTED = 'not-granted'
PERM_NOT_SET = 'not-set'


class ForumAdmin(admin.ModelAdmin):
    """
    The ForumAdmin class provides a specific view for moving up or down any forums.
    """
    fieldsets = (
        [None, {
            'fields': ('type', 'parent', 'name', 'description', 'image',)
        }],
        [_('Forum settings'), {
            'fields': ('display_sub_forum_list',),
            'classes': ('collapse',)
        }],
        [_('Link forum settings'), {
            'fields': ('link', 'link_redirects',),
            'classes': ('collapse',)
        }],
    )
    list_display = ('name', 'type', 'topics_count', 'posts_count',)
    search_fields = ('name',)

    editpermissions_index_view_template_name = 'admin/forum/forum/editpermissions_index.html'
    editpermissions_user_view_template_name = 'admin/forum/forum/editpermissions_user.html'
    editpermissions_anonymous_user_view_template_name = 'admin/forum/forum/editpermissions_anonymous_user.html'
    editpermissions_group_view_template_name = 'admin/forum/forum/editpermissions_group.html'

    def get_urls(self):
        urls = super(ForumAdmin, self).get_urls()
        forum_admin_urls = patterns(
            '',
            url(r'^(?P<forum_id>[0-9]+)/move-forum/(?P<direction>up|down)/$',
                self.admin_site.admin_view(self.moveforum_view),
                name='forum_forum_move'),
            url(r'^(?P<forum_id>[0-9]+)/edit-permissions/$',
                self.admin_site.admin_view(self.editpermissions_index_view),
                name='forum_forum_editpermission_index'),
            url(r'^(?P<forum_id>[0-9]+)/edit-permissions/user/(?P<user_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_user_view),
                name='forum_forum_editpermission_user'),
            url(r'^(?P<forum_id>[0-9]+)/edit-permissions/user/anonymous/$',
                self.admin_site.admin_view(self.editpermissions_anonymous_user_view),
                name='forum_forum_editpermission_anonymous_user'),
            url(r'^(?P<forum_id>[0-9]+)/edit-permissions/group/(?P<group_id>[0-9]+)/$',
                self.admin_site.admin_view(self.editpermissions_group_view),
                name='forum_forum_editpermission_group'),
        )
        return forum_admin_urls + urls

    def get_forum_perms_base_context(self, request, obj):
        """
        Returns context dictionary with common admin and object permissions
        related content.
        """
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
        """
        Moves the given forum toward the requested direction.
        """
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

    def editpermissions_index_view(self, request, forum_id):
        """
        Display a form to select a user or a group in order to edit its
        permissions for the considered forum.
        """
        forum = get_object_or_404(Forum, pk=forum_id)

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = _('Forum permissions')

        if request.method == 'POST':
            user_form = PickUserForm(request.POST, admin_site=self.admin_site)
            group_form = PickGroupForm(request.POST, admin_site=self.admin_site)

            if user_form.is_valid() and group_form.is_valid():
                user = user_form.cleaned_data.get('user', None) \
                    if user_form.cleaned_data else None
                anonymous_user = user_form.cleaned_data.get('anonymous_user', None) \
                    if user_form.cleaned_data else None
                group = group_form.cleaned_data.get('group', None) \
                    if group_form.cleaned_data else None

                if not user and not anonymous_user and not group:
                    user_form._errors[NON_FIELD_ERRORS] = user_form.error_class(
                        [_('Choose either a user ID, a group ID or the anonymous user'), ])
                elif user:
                    # Redirect to user
                    return redirect(reverse(
                        'admin:forum_forum_editpermission_user',
                        args=(forum.id, user.id)))
                elif anonymous_user:
                    # Redirect to anonymous user
                    return redirect(reverse(
                        'admin:forum_forum_editpermission_anonymous_user',
                        args=(forum.id,)))
                elif group:
                    # Redirect to group
                    return redirect(reverse(
                        'admin:forum_forum_editpermission_group',
                        args=(forum.id, group.id)))

            context['user_errors'] = helpers.AdminErrorList(user_form, [])
            context['group_errors'] = helpers.AdminErrorList(group_form, [])
        else:
            user_form = PickUserForm(admin_site=self.admin_site)
            group_form = PickGroupForm(admin_site=self.admin_site)

        context['user_form'] = user_form
        context['group_form'] = group_form

        return render(
            request, self.editpermissions_index_view_template_name, context)

    def editpermissions_user_view(self, request, forum_id, user_id):
        """
        Display a form to define which permissions are granted for the given user
        for the considered forum.
        """
        user_model = get_user_model()
        user = get_object_or_404(user_model, pk=user_id)
        forum = get_object_or_404(Forum, pk=forum_id)

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), user)
        context['form'] = self._get_permissions_form(
            request, UserForumPermission, {'forum': forum, 'user': user})

        return render(
            request, self.editpermissions_user_view_template_name, context)

    def editpermissions_anonymous_user_view(self, request, forum_id):
        """
        Display a form to define which permissions are granted for the anonymous user
        for the considered forum.
        """
        forum = get_object_or_404(Forum, pk=forum_id)

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), _('Anonymous user'))
        context['form'] = self._get_permissions_form(
            request, UserForumPermission, {'forum': forum, 'anonymous_user': True})

        return render(
            request, self.editpermissions_anonymous_user_view_template_name, context)

    def editpermissions_group_view(self, request, forum_id, group_id):
        """
        Display a form to define which permissions are granted for the given group
        for the considered forum.
        """
        group = get_object_or_404(Group, pk=group_id)
        forum = get_object_or_404(Forum, pk=forum_id)

        # Set up the context
        context = self.get_forum_perms_base_context(request, forum)
        context['forum'] = forum
        context['title'] = '{} - {}'.format(_('Forum permissions'), group)
        context['form'] = self._get_permissions_form(
            request, GroupForumPermission, {'forum': forum, 'group': group})

        return render(
            request, self.editpermissions_group_view_template_name, context)

    def _get_permissions_form(self, request, permission_model, filter_kwargs):
        # Fetch the permissions
        editable_permissions = ForumPermission.objects.filter(is_local=True) \
            .order_by('name')
        granted_permissions = permission_model.objects.filter(
            permission__in=editable_permissions, has_perm=True, **filter_kwargs) \
            .values_list('permission__codename', flat=True)
        non_granted_permissions = permission_model.objects.filter(
            permission__in=editable_permissions, has_perm=False, **filter_kwargs) \
            .values_list('permission__codename', flat=True)

        permissions_dict = OrderedDict()
        for p in editable_permissions:
            if p.codename in granted_permissions:
                perm_state = PERM_GRANTED
            elif p.codename in non_granted_permissions:
                perm_state = PERM_NOT_GRANTED
            else:
                perm_state = PERM_NOT_SET
            permissions_dict[p.codename] = (p, perm_state)

        if request.method == 'POST':
            form = PermissionsForm(request.POST, permissions_dict=permissions_dict)
            if form.is_valid():
                for codename, value in form.cleaned_data.items():
                    try:
                        perm = permission_model.objects.get(
                            permission=permissions_dict[codename][0], **filter_kwargs)
                    except permission_model.DoesNotExist:
                        if value == PERM_NOT_SET:
                            continue
                        perm = permission_model.objects.create(
                            permission=permissions_dict[codename][0], **filter_kwargs)

                    if value == PERM_NOT_SET:
                        perm.delete()
                        continue

                    perm.has_perm = (value == PERM_GRANTED)
                    perm.save()

                self.message_user(request, _('Permissions successfully applied'))
        else:
            form = PermissionsForm(permissions_dict=permissions_dict)

        return form


class PickUserForm(forms.Form):
    user = UserForumPermission._meta.get_field('user').formfield()
    anonymous_user = forms.BooleanField(
        label=_('Anonymous'),
        initial=False,
        help_text=_('Please select this option if you want to edit the permissions of the anonymous user'))

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop('admin_site')
        super(PickUserForm, self).__init__(*args, **kwargs)

        self.fields['user'].required = False
        self.fields['user'].widget = ForeignKeyRawIdWidget(
            UserForumPermission._meta.get_field('user').rel,
            admin_site)

        self.fields['anonymous_user'].required = False

    def clean(self):
        cleaned_data = super(PickUserForm, self).clean()
        user = cleaned_data.get('user', None)
        anonymous_user = cleaned_data.get('anonymous_user', None)
        if user and anonymous_user:
            self._errors[NON_FIELD_ERRORS] = self.error_class(
                [_('Choose either a user ID or select the anonymous user'), ])
        return cleaned_data


class PickGroupForm(forms.Form):
    group = GroupForumPermission._meta.get_field('group').formfield()

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop('admin_site')
        super(PickGroupForm, self).__init__(*args, **kwargs)

        self.fields['group'].required = False
        self.fields['group'].widget = ForeignKeyRawIdWidget(
            GroupForumPermission._meta.get_field('group').rel,
            admin_site)


class PermissionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.permissions_dict = kwargs.pop('permissions_dict', {})
        super(PermissionsForm, self).__init__(*args, **kwargs)

        # Initializes permission fields
        f_choices = (
            (PERM_NOT_SET, _('Not set')),
            (PERM_GRANTED, _('Granted')),
            (PERM_NOT_GRANTED, _('Not granted')),
        )
        for codename, p in self.permissions_dict.items():
            self.fields[codename] = forms.ChoiceField(
                label=p[0].name,
                choices=f_choices,
                required=False,
                widget=forms.RadioSelect)
            self.fields[codename].initial = p[1]


admin.site.register(Forum, ForumAdmin)
