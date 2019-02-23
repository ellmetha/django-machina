import os

from django import VERSION as DJANGO_VERSION

from machina import MACHINA_MAIN_STATIC_DIR, MACHINA_MAIN_TEMPLATE_DIR


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'nomigrations'


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
    MIGRATION_MODULES = DisableMigrations() if DJANGO_VERSION < (1, 11) else {}
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
            'TEST': {
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_general_ci',
            },
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            location('_testsite/templates'),
            MACHINA_MAIN_TEMPLATE_DIR,
        ),
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                # Machina
                'machina.core.context_processors.metadata',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'mptt',
    'haystack',
    'widget_tweaks',
    'tests',

    # Machina apps.
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
    'tests._testsite.apps.forum_conversation',
)

SITE_ID = 1

ROOT_URLCONF = 'tests._testsite.urls'

if DJANGO_VERSION >= (1, 10):
    MIDDLEWARE = (
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
else:
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
