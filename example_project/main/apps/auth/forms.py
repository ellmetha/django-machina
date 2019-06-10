from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _


class UserCreationForm(UserCreationForm):
    email = EmailField(label=_('Email address'), required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserParametersForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def __init__(self, *args, **kwargs):
        super(UserParametersForm, self).__init__(*args, **kwargs)
        # Update some fields
        self.fields['email'].required = True


class UserDeletionForm(forms.Form):
    username = forms.CharField(label='', max_length=254)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserDeletionForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = _('Type your username')

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.user.username:
            self.add_error('username', _('Please type your username to remove your account'))
        return username
