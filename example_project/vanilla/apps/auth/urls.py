# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^account/parameters/edit/',
        views.UserAccountParametersUpdateView.as_view(), name='account-parameters'),
    url(r'^account/password/edit/',
        views.UserPasswordUpdateView.as_view(), name='account-password'),
    url(r'^register/', views.UserCreateView.as_view(), name='register'),
    url(r'^unregister/', views.UserDeleteView.as_view(), name='unregister'),
]
