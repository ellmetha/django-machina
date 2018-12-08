from django.urls import include, path

from . import views


urlpatterns = [
    path('account/', include('django.contrib.auth.urls')),
    path(
        'account/parameters/edit/',
        views.UserAccountParametersUpdateView.as_view(),
        name='account-parameters',
    ),
    path(
        'account/password/edit/',
        views.UserPasswordUpdateView.as_view(),
        name='account-password',
    ),
    path(
        'register/',
        views.UserCreateView.as_view(),
        name='register',
    ),
    path(
        'unregister/',
        views.UserDeleteView.as_view(),
        name='unregister',
    ),
]
