from django.conf import settings
from django.conf.urls import static
from django.urls import include, path
from django.views.generic import RedirectView

from django_yunohost_integration.yunohost_utils import SSOwatLoginRedirectView


# settings.PATH_URL is the $YNH_APP_ARG_PATH
# Prefix all urls with "PATH_URL":
urlpatterns = [
    path('', RedirectView.as_view(url=f'{settings.PATH_URL}/')),
    path(f'{settings.PATH_URL}/', include('django_example.urls')),
    #
    # Cover over the default Django Admin Login with SSOWat login:
    path(f'{settings.PATH_URL}/login/', SSOwatLoginRedirectView.as_view(), name='ssowat-login'),
]


if settings.SERVE_FILES:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
