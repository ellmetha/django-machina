"""
    Forum forms
    ===========

    This module defines forms provided by the ``forum`` application.

"""

from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _
from mptt.forms import TreeNodeChoiceField

from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')

PermissionConfig = get_class('forum_permission.defaults', 'PermissionConfig')


class PickUserForm(forms.Form):
    """ Form allowing to pick a user to edit their permissions. """

    user = UserForumPermission._meta.get_field('user').formfield()
    anonymous_user = forms.BooleanField(
        label=_('Anonymous'),
        initial=False,
        help_text=_(
            'Please select this option if you want to edit the permissions of the anonymous user'
        ),
    )
    authenticated_user = forms.BooleanField(
        label=_('Authenticated'),
        initial=False,
        help_text=_(
            'Please select this option if you want to edit the permissions of every ' +
            '(non-specific) logged in user'
        ),
    )

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop('admin_site')
        super().__init__(*args, **kwargs)

        self.fields['user'].required = False
        self.fields['user'].widget = ForeignKeyRawIdWidget(
            UserForumPermission._meta.get_field('user').remote_field, admin_site,
        )

        self.fields['anonymous_user'].required = False
        self.fields['authenticated_user'].required = False

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user', None)
        anonymous_user = cleaned_data.get('anonymous_user', None)
        authed_user = cleaned_data.get('authenticated_user', None)
        if (user and anonymous_user) or (user and authed_user) or (anonymous_user and authed_user):
            self._errors[NON_FIELD_ERRORS] = self.error_class([
                _(
                    'Choose either a user ID or check either the anonymous or ' +
                    'authenticated user checkbox'
                ),
            ],)
        return cleaned_data


class PickGroupForm(forms.Form):
    """ Form allowing to pick a group to edit its permissions. """

    group = GroupForumPermission._meta.get_field('group').formfield()

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop('admin_site')
        super().__init__(*args, **kwargs)

        self.fields['group'].required = False
        self.fields['group'].widget = ForeignKeyRawIdWidget(
            GroupForumPermission._meta.get_field('group').remote_field, admin_site,
        )


class PickForumForm(forms.Form):
    """ Form allowing to pick a specific forum. """

    forum = TreeNodeChoiceField(queryset=Forum.objects.all(), required=False)


class PermissionsForm(forms.Form):
    """ Form allowing to edit permissions. """

    PERM_GRANTED = 'granted'
    PERM_NOT_GRANTED = 'not-granted'
    PERM_NOT_SET = 'not-set'

    def __init__(self, *args, **kwargs):
        self.permissions_dict = kwargs.pop('permissions_dict', {})
        super().__init__(*args, **kwargs)

        # Initializes permission fields
        f_choices = (
            (self.PERM_NOT_SET, _('Not set')),
            (self.PERM_GRANTED, _('Granted')),
            (self.PERM_NOT_GRANTED, _('Not granted')),
        )
        for scope in PermissionConfig.scopes:
            codenames = [
                x['codename'] for x in PermissionConfig.permissions if x['scope'] == scope
            ]
            permissions = filter(lambda v: v[0] in codenames, self.permissions_dict.items())
            for codename, p in permissions:
                self.fields[codename] = forms.ChoiceField(
                    label=p[0].name, choices=f_choices, required=False, widget=forms.RadioSelect,
                )
                self.fields[codename].initial = p[1]
                self.fields[codename].scope = scope
