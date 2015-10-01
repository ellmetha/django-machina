# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.edit import CreateView
from machina.app import board

# Local application / specific library imports
from example_project.views import UserAccountParametersUpdateView
from example_project.views import UserCreateView


# Admin autodiscover
admin.autodiscover()

# Patterns
urlpatterns = patterns(
    '',

    # Admin
    url(r'^' + settings.ADMIN_URL, include(admin.site.urls)),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^account/edit/parameters/', UserAccountParametersUpdateView.as_view(), name='account-parameters'),
    url('^register/', UserCreateView.as_view(), name='register'),
    url('^markdown/', include( 'django_markdown.urls')),

    # Apps
    url(r'', include(board.urls)),
)

# # In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns(
        '',
        url(r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
