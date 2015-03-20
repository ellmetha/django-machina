# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.views.generic.edit import CreateView

# Local application / specific library imports
from example_project.forms import UserCreationForm


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
