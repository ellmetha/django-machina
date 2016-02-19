# -*- coding: utf-8 -*-

import os

from machina import get_apps as get_machina_apps
from machina import MACHINA_MAIN_STATIC_DIR
from machina import MACHINA_MAIN_TEMPLATE_DIR


TEST_ROOT = os.path.abspath(os.path.dirname(__file__))

# Helper function to extract absolute path
location = lambda x: os.path.join(TEST_ROOT, x)


DEBUG = False
TEMPLATE_DEBUG = False

DB_CONFIG = os.environ.get('DB', 'sqlite')

if DB_CONFIG == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }
elif DB_CONFIG == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'machina_test',
            'USER': 'postgres',
        }
    }
elif DB_CONFIG == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'machina_test',
            'USER': 'root',
        }
    }

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    # Machina
    'machina.core.context_processors.metadata',
)

TEMPLATE_DIRS = (
    location('_testsite/templates'),
    MACHINA_MAIN_TEMPLATE_DIR,
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'mptt',
    'haystack',
    'widget_tweaks',
    'django_markdown',
    'tests',
] + get_machina_apps(['tests._testsite.apps.forum_conversation', ])

SITE_ID = 1

ROOT_URLCONF = 'tests._testsite.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Machina
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
)

ADMINS = ('admin@example.com',)

MEDIA_ROOT = os.path.join(TEST_ROOT, '_testdata/media/')
STATIC_ROOT = os.path.join(TEST_ROOT, '_testdata/static/')

STATICFILES_DIRS = (
    MACHINA_MAIN_STATIC_DIR,
)

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

LOGIN_REDIRECT_URL = '/accounts/'

STATIC_URL = '/static/'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(TEST_ROOT, '_testdata/whoosh_index'),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp',
    }
}

# Setting this explicitly prevents Django 1.7+ from showing a
# warning regarding a changed default test runner. The test
# suite is run with py.test, so it does not matter.
SILENCED_SYSTEM_CHECKS = ['1_6.W001']

SECRET_KEY = 'key'

try:
    from .settings_local import *  # noqa
except ImportError:
    pass
