# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test.client import Client
import pytest


@pytest.mark.django_db
class BaseClientTestCase(object):
    """
    Shortcut class for using Django's test client and avoid boilerplate code
    such as user login or user creation.
    """
    username = 'dummyuser'
    email = 'dummyuser@example.com'
    password = 'dummypassword'
    is_anonymous = False
    is_staff = False
    is_superuser = False
    permissions = []

    @pytest.fixture(autouse=True)
    def _setup_client(self):
        self.client = Client()
        if not self.is_anonymous:
            self.login()

    def login(self):
        self.user = self.create_user()
        self.client.login(username=self.username,
                          password=self.password)

    def create_user(self, username=None, password=None, email=None,
                    is_staff=None, is_superuser=None, permissions=None):
        user = User.objects.create_user(username or self.username,
                                        email or self.email,
                                        password or self.password)
        user.is_staff = is_staff or self.is_staff
        user.is_superuser = is_superuser or self.is_superuser
        user.save()
        return user


class AdminClientTestCase(BaseClientTestCase):
    is_staff = True
    is_superuser = True
