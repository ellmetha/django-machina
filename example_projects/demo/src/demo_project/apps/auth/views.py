# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView

# Local application / specific library imports
from demo_project.core.mixins import MenuItemMixin
from demo_project.forms import UserCreationForm
from demo_project.forms import UserParametersForm


class UserCreateView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm

    success_url = '/'

    def form_valid(self, form):
        response = super(UserCreateView, self).form_valid(form)

        # We log the user in
        new_authenticated_user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'])
        login(self.request, new_authenticated_user)

        return response


class UserAccountParametersUpdateView(MenuItemMixin, UpdateView):
    model = User
    form_class = UserParametersForm
    template_name = 'registration/parameters.html'
    menu_parameters = 'account'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserAccountParametersUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Your account has been successfully updated'))
        return super(UserAccountParametersUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('account-parameters')


class UserPasswordUpdateView(MenuItemMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'registration/password.html'
    menu_parameters = 'password'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserPasswordUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(UserPasswordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Your password has been successfully updated'))
        return super(UserPasswordUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('account-password')
