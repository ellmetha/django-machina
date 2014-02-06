# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import include
from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Local application / specific library imports
from machina.app import board


admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'', include(board.urls)),
)
urlpatterns += staticfiles_urlpatterns()
