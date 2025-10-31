import base64
import logging
from pathlib import Path
from urllib.parse import ParseResult, urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest, host_validation_re
from django.views import View


try:
    from django.contrib.auth.views import RedirectURLMixin  # New in Django 4.1
except ImportError:
    # Django 4.0 fallback:
    from django_yunohost_integration.compat import RedirectURLMixin


logger = logging.getLogger(__name__)

YNH_CURRENT_HOST = '/etc/yunohost/current_host'


class YnhCurrentHostError(Exception):
    pass


def get_ssowat_domain() -> str:
    path = Path(YNH_CURRENT_HOST)
    if not path.is_file():
        raise YnhCurrentHostError(f'No such file: {YNH_CURRENT_HOST!r}')

    try:
        current_host = path.read_text()
    except Exception as err:
        logger.exception(f'Cannot read {YNH_CURRENT_HOST!r}: %s', err)
        raise YnhCurrentHostError(f'Cannot read {YNH_CURRENT_HOST!r}: {err}')

    current_host = current_host.strip()
    if not current_host:
        raise YnhCurrentHostError(f'{YNH_CURRENT_HOST!r} is empty')

    if not host_validation_re.match(current_host):
        raise YnhCurrentHostError(f'{current_host!r} is invalid')

    return current_host


def encode_ssowat_uri(uri: str) -> str:
    uri_bytes = uri.encode(encoding='UTF8')
    uri_encoded_bytes: bytes = base64.urlsafe_b64encode(uri_bytes)
    uri_encoded = uri_encoded_bytes.decode(encoding='ASCII')
    return uri_encoded


def build_ssowat_uri(request: HttpRequest, next_url: str) -> str:
    user = request.user
    assert not user.is_authenticated, 'User "{user}" already authenticated'

    result: ParseResult = urlparse(next_url)
    if result.scheme:
        raise ValueError(f'{next_url=} should not contain {result.scheme=} part')
    if result.netloc:
        raise ValueError(f'{next_url=} should not contain {result.netloc=} part')

    next_uri = f'{request.scheme}://{request.get_host()}{next_url.lstrip("/")}'
    next_uri_base64 = encode_ssowat_uri(next_uri)

    try:
        ynh_sso_host = get_ssowat_domain()
    except YnhCurrentHostError as err:
        logger.exception(str(err))
        ynh_sso_host = request.get_host()

    ssowat_uri = f'{request.scheme}://{ynh_sso_host}/yunohost/sso/?r={next_uri_base64}'
    return ssowat_uri


class SSOwatLoginRedirectView(RedirectURLMixin, View):
    """
    This view should be registered in urls with LOGIN_URL and should cover
    the Django Admin Login view, too.
    e.g.:

        urlpatterns = [
            path('admin/login/', SSOwatLoginRedirectView.as_view(), name='ssowat-login'),
            path('admin/', admin.site.urls),
        ]
        settings.LOGIN_URL='/yunohost/sso/'
        settings.LOGIN_REDIRECT_URL='/yunohost/sso/'
    """

    next_page = settings.LOGIN_REDIRECT_URL
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_allowed_hosts = set()

    def get(self, request: HttpRequest):
        user = request.user
        next_url = self.get_success_url()
        if user.is_authenticated:
            logger.info('User "%s" already authenticated: Redirect to: %s', user, next_url)
            return HttpResponseRedirect(next_url)

        ssowat_uri = build_ssowat_uri(request, next_url)
        logger.info('Redirect to SSOwat login with return URI: "%s"', next_url)
        return HttpResponseRedirect(ssowat_uri)
