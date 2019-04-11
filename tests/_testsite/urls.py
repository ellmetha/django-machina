from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from machina import urls as machina_urls


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(machina_urls)),
]
urlpatterns += staticfiles_urlpatterns()
