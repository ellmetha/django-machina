# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

# Local application / specific library imports


def add_permissions(user, permissions):
    """
    Add a set of permissions to a given user.
    """
    for permission in permissions:
        app_label, _, codename = permission.partition('.')
        perm = Permission.objects.get(content_type__app_label=app_label,
                                      codename=codename)
        user.user_permissions.add(perm)


class BaseClientTestCase(TestCase):
    """
    Shortcut TestCase for using Django's test client and avoid boilerplate code
    such as user login or user creation.
    """
    username = 'dummyuser'
    email = 'dummyuser@example.com'
    password = 'dummypassword'
    is_anonymous = False
    is_staff = False
    is_superuser = False
    permissions = []

    def setUp(self):
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
        perms = permissions if permissions is not None else self.permissions
        add_permissions(user, perms)
        return user

    def assertIsOk(self, response):
        self.assertEqual(200, response.status_code)

    def assertNoAccess(self, response):
        self.assertTrue(response.status_code in (404, 403))
