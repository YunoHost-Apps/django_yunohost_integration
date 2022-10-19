from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


# settings.PATH_URL is the $YNH_APP_ARG_PATH
# Prefix all urls with "PATH_URL":
urlpatterns = [
    path('', RedirectView.as_view(url=f'{settings.PATH_URL}/')),
    path(f'{settings.PATH_URL}/', include('django_example.urls')),
    path(f'{settings.PATH_URL}/', admin.site.urls),
]
