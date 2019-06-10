from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from machina import urls as machina_urls


js_info_dict = {
    'packages': ('base', ),
}

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript_catalog'),

    # Admin
    path(settings.ADMIN_URL, admin.site.urls),

    # Apps
    path('', include('main.apps.auth.urls')),
    path('', include(machina_urls)),
]

if settings.DEBUG:
    # Add the Debug Toolbar’s URLs to the project’s URLconf
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)), ]

    # In DEBUG mode, serve media files through Django.
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views import static
    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += [
        re_path(r'^%s/(?P<path>.*)$' % media_url, static.serve,
                {'document_root': settings.MEDIA_ROOT}),
    ]
