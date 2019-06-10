from .base import *  # noqa


# APP CONFIGURATION
# ------------------------------------------------------------------------------

INSTALLED_APPS += (  # noqa: F405
    'debug_toolbar',
)


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------

MIDDLEWARE += (  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


# DEBUG CONFIGURATION
# ------------------------------------------------------------------------------

DEBUG = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', ]
INTERNAL_IPS = ['127.0.0.1', ]


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------

TEMPLATES[0]['OPTIONS']['loaders'] = (  # noqa: F405
    # Disables cached loader
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------

STATICFILES_DIRS = (
    MACHINA_MAIN_STATIC_DIR,  # noqa: F405
    str(PROJECT_PATH / 'main' / 'static'),  # noqa: F405
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
