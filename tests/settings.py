# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
from django.conf import settings

# Local application / specific library imports
from machina import get_vanilla_apps
from machina import MACHINA_MAIN_TEMPLATE_DIR


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

# Helper function to extract absolute path
location = lambda x: os.path.join(TEST_ROOT, x)


TEST_SETTINGS = {
    'DEBUG': False,
    'TEMPLATE_DEBUG': False,
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    'TEMPLATE_CONTEXT_PROCESSORS': (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.request',
        # Machina
        'machina.core.context_processors.metadata',
    ),
    'TEMPLATE_DIRS': (
        location('_testsite/templates'),
        MACHINA_MAIN_TEMPLATE_DIR,
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
        'haystack',
        'bootstrap3',
        'compressor',
        'django_markdown',
        'easy_thumbnails',
        'tests',
    ] + get_vanilla_apps(['tests._testsite.apps.forum_conversation', ]),
    'SITE_ID': 1,
    'ROOT_URLCONF': 'tests._testsite.urls',
    'MIDDLEWARE_CLASSES': (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    'ADMINS': ('admin@example.com',),
    'MEDIA_ROOT': os.path.join(TEST_ROOT, '_testdata/media/'),
    'STATIC_ROOT': os.path.join(TEST_ROOT, '_testdata/static/'),
    'PASSWORD_HASHERS': ['django.contrib.auth.hashers.MD5PasswordHasher'],
    'LOGIN_REDIRECT_URL': '/accounts/',
    'STATIC_URL': '/static/',
    'ANONYMOUS_USER_ID': -1,
    'HAYSTACK_CONNECTIONS': {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    },
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'machina_attachments': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp',
        }
    },

    # Setting this explicitly prevents Django 1.7+ from showing a
    # warning regarding a changed default test runner. The test
    # suite is run with nose, so it does not matter.
    'SILENCED_SYSTEM_CHECKS': ['1_6.W001'],
}


def configure():
    if not settings.configured:
        settings.configure(**TEST_SETTINGS)
