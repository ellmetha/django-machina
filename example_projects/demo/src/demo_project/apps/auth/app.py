# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include
from django.conf.urls import url
from machina.core.app import Application

from demo_project.apps.auth import views


class AuthApp(Application):
    name = None

    user_create_view = views.UserCreateView
    user_parameters_update_view = views.UserAccountParametersUpdateView
    user_password_update_view = views.UserPasswordUpdateView
    user_delete_view = views.DeleteUserView

    def get_urls(self):
        return [
            url(r'^', include('django.contrib.auth.urls')),
            url(r'^parameters/edit/', self.user_parameters_update_view.as_view(), name='account-parameters'),
            url(r'^password/edit/', self.user_password_update_view.as_view(), name='account-password'),
            url(r'^register/', self.user_create_view.as_view(), name='register'),
            url(r'^unregister/$', self.user_delete_view.as_view(), name='unregister'),
        ]


application = AuthApp()
