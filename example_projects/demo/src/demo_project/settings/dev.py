from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
]

INTERNAL_IPS = (
    '127.0.0.1',
)

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
)
