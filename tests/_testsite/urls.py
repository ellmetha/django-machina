from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from machina import urls as machina_urls


admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(machina_urls)),
]
urlpatterns += staticfiles_urlpatterns()
