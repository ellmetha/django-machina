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
        'django.core.context_processors.request',
    ),
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.admin',
        'tests',
    ] + get_vanilla_apps(),
    'SITE_ID': 3,
    'MEDIA_ROOT': os.path.join(TEST_ROOT, '_testdata/media/'),
}


def configure():
    if not settings.configured:
        settings.configure(**TEST_SETTINGS)
