import base64
import logging
from urllib.parse import ParseResult, unquote, urlparse

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import RedirectURLMixin
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.views import View


logger = logging.getLogger(__name__)


def encode_ssowat_uri(uri: str) -> str:
    """
    Encode the given URI as urlsafe base64 string useable for SSOwat redirect URIs.
    >>> encode_ssowat_uri('/foo/bar/')
    'L2Zvby9iYXIv'
    """
    uri_bytes = uri.encode(encoding='UTF8')
    uri_encoded_bytes: bytes = base64.urlsafe_b64encode(uri_bytes)
    uri_encoded = uri_encoded_bytes.decode(encoding='ASCII')
    return uri_encoded


def decode_ssowat_uri(encoded_uri: str) -> str:
    """
    Decode a base64-encoded SSOwat URI.
    >>> decode_ssowat_uri('L2Zvby9iYXIv')
    '/foo/bar/'
    """
    # Decode URL-encoded string first
    encoded_uri = unquote(encoded_uri)
    # Add padding if necessary
    missing_padding = len(encoded_uri) % 4
    if missing_padding:
        encoded_uri += '=' * (4 - missing_padding)
    uri_bytes = base64.urlsafe_b64decode(encoded_uri.encode('ASCII'))
    uri = uri_bytes.decode('UTF8')
    return uri


def build_ssowat_uri(request: HttpRequest, next_url: str) -> str:
    user = request.user
    assert not user.is_authenticated, 'User "{user}" already authenticated'

    next_uri = f'{request.scheme}://{request.get_host()}/'

    if next_url != '/':
        result: ParseResult = urlparse(next_url)
        if result.scheme:
            raise ValueError(f'{next_url=} should not contain {result.scheme=} part')
        if result.netloc:
            raise ValueError(f'{next_url=} should not contain {result.netloc=} part')

        next_uri = f'{next_uri}{next_url.strip("/")}/'
    logger.debug('Built SSOWat next_uri=%r', next_uri)
    next_uri_base64 = encode_ssowat_uri(next_uri)

    ssowat_uri = f'/yunohost/sso/?r={next_uri_base64}'
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
        settings.LOGIN_REDIRECT_URL='/app_path/'
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
