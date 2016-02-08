# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from demo_project.apps.app import application


# Admin autodiscover
admin.autodiscover()

# Patterns
urlpatterns = [
    # Admin
    url(r'^' + settings.ADMIN_URL, include(admin.site.urls)),

    # Apps
    url(r'', include(application.urls)),
]

# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    from django.views.static import serve
    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += [
        url(r'^%s/(?P<path>.*)$' % media_url, serve, {'document_root': settings.MEDIA_ROOT}),
    ]
