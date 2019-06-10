import pathlib

from django.urls import reverse_lazy

from machina import MACHINA_MAIN_STATIC_DIR
from machina import MACHINA_MAIN_TEMPLATE_DIR


PROJECT_PATH = pathlib.Path(__file__).parents[2]


# APP CONFIGURATION
# ------------------------------------------------------------------------------

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Third party apps
    'mptt',
    'haystack',
    'widget_tweaks',

    # Machina apps
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
)


# MIGRATION CONFIGURATION
# ------------------------------------------------------------------------------

MIGRATION_MODULES = {
    'forum_conversation': 'machina.apps.forum_conversation.migrations',
    'forum_member': 'machina.apps.forum_member.migrations',
}


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------

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


# DEBUG CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False


# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(PROJECT_PATH / 'test.db'),
    }
}


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'EST'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#languages
LANGUAGES = (
    ('en', 'English'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = (
    str(PROJECT_PATH / 'project' / 'locale'),
)


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'NOTSECRET'


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            str(PROJECT_PATH / 'main' / 'templates'),
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
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            ]
        },
    },
]


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(PROJECT_PATH / 'public' / 'static')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    MACHINA_MAIN_STATIC_DIR,
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(PROJECT_PATH / 'public' / 'media')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'


# URL CONFIGURATION
# ------------------------------------------------------------------------------

ROOT_URLCONF = 'project.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'


# ADMIN CONFIGURATION
# ------------------------------------------------------------------------------

# URL of the admin page
ADMIN_URL = 'admin/'


# AUTH CONFIGURATION
# ------------------------------------------------------------------------------

LOGIN_URL = reverse_lazy('login')


# CACHE CONFIGURATION
# ------------------------------------------------------------------------------

# Attachment cache backend
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp',
    }
}


# CKEDITOR CONFIGURATION
# ------------------------------------------------------------------------------

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo', ]},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley',
             'SpecialChar', 'PageBreak', ]},
            {'name': 'styles', 'items': ['Styles', 'Format', ]},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Strike', '-', 'RemoveFormat', ]},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent',
             'Indent', '-', 'Blockquote', ]},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor', ]},
            {'name': 'tools', 'items': ['Maximize', ]},
        ],
    }
}


# HAYSTACK CONFIGURATION
# ------------------------------------------------------------------------------

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': str(PROJECT_PATH / 'whoosh_index'),
    },
}


# MACHINA SETTINGS
# ------------------------------------------------------------------------------

MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = [
    'can_see_forum',
    'can_read_forum',
    'can_start_new_topics',
    'can_reply_to_topics',
    'can_edit_own_posts',
    'can_post_without_approval',
    'can_create_polls',
    'can_vote_in_polls',
    'can_download_file',
]
