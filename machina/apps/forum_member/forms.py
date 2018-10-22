"""
    Forum member forms
    ==================

    This module defines forms provided by the ``forum_member`` application.

"""

from django import forms

from machina.conf import settings as machina_settings
from machina.core.db.models import get_model


ForumProfile = get_model('forum_member', 'ForumProfile')


class ForumProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not machina_settings.PROFILE_AVATARS_ENABLED:
            del self.fields["avatar"]

    class Meta:
        model = ForumProfile
        fields = ['avatar', 'signature', ]
