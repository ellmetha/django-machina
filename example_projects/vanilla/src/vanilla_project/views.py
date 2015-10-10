# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

# Local application / specific library imports
from vanilla_project.forms import UserCreationForm
from vanilla_project.forms import UserParametersForm


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


class UserAccountParametersUpdateView(UpdateView):
    model = User
    form_class = UserParametersForm
    template_name = 'registration/parameters.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserAccountParametersUpdateView, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Your account has been successfully updated'))
        return super(UserAccountParametersUpdateView, self).form_valid(form)

    def get_success_url(self):
        return '/'
