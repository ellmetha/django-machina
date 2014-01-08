# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from django.conf import global_settings as default_settings
from django.conf import settings

# Local application / specific library imports
from machina import get_vanilla_apps


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))


TEST_SETTINGS = {
    'DEBUG': False,
    'TEMPLATE_DEBUG': False,
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    'TEMPLATE_LOADERS': (
        'django.template.loaders.app_directories.Loader',
    ),
    'TEMPLATE_CONTEXT_PROCESSORS': default_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.request',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
    ),
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.messages',
        'django.contrib.sessions',
        'django.contrib.sites',
        'mptt',
        'guardian',
        'tests',
    ] + get_vanilla_apps(),
    'ROOT_URLCONF': 'tests._testsite.urls',
    'MIDDLEWARE_CLASSES': default_settings.MIDDLEWARE_CLASSES,
    'SITE_ID': 1,
    'ADMINS': ('admin@example.com',),
    'MEDIA_ROOT': os.path.join(TEST_ROOT, '_testdata/media/'),
    'PASSWORD_HASHERS': ['django.contrib.auth.hashers.MD5PasswordHasher'],
    'LOGIN_REDIRECT_URL': '/accounts/',
    'STATIC_URL': '/static/',
    'ANONYMOUS_USER_ID': -1,
}


def configure():
    if not settings.configured:
        settings.configure(**TEST_SETTINGS)
