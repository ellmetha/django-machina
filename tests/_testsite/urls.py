# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from machina.app import board


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(board.urls)),
]
urlpatterns += staticfiles_urlpatterns()
