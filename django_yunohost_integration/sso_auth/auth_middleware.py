import base64
import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import RemoteUserMiddleware

from django_yunohost_integration.yunohost.ynh_jwt import verify_sso_jwt


try:
    from axes.exceptions import AxesBackendPermissionDenied as SuspiciousOperation  # log to Axes DB models
except ImportError:
    from django.core.exceptions import SuspiciousOperation

from django_yunohost_integration.sso_auth.user_profile import call_setup_user, update_user_profile


logger = logging.getLogger(__name__)


UserModel = get_user_model()


class SSOwatRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Middleware to login a user via HTTP_YNH_USER header, added by nginx config:

        proxy_set_header Ynh-User $http_ynh_user;

    But additionally check also:
     - JWT token from SSOwat cookie `yunohost.portal`
     - HTTP_AUTHORIZATION header with basic auth info (Check username only)

    Use Django Axes if something is wrong.
    Update exising user information.
    """

    header = settings.YNH_USER_NAME_HEADER_KEY
    force_logout_if_no_header = True

    def process_request(self, request):
        if self.header not in request.META:
            logger.warning('Missing %r header', self.header)
        else:
            logger.debug('%r header value: %r', self.header, request.META[self.header])

        # Keep the information if the user is already logged in
        was_authenticated = request.user.is_authenticated

        super().process_request(request)  # login remote user

        user = request.user

        if not user.is_authenticated:
            logger.debug('Not logged in -> nothing to verify here')
            return

        # Check SSOwat cookie informations:
        try:
            sso_jwt_data = request.COOKIES[settings.YNH_JWT_COOKIE_NAME]
        except KeyError:
            logger.error('%r cookie missing!', settings.YNH_JWT_COOKIE_NAME)

            if settings.DEBUG:
                # e.g.: local test can't set a Cookie easily
                logger.warning('Ignore error, because settings.DEBUG is on!')
            else:
                # emits a signal indicating user login failed, which is processed by
                # axes.signals.log_user_login_failed which logs and flags the failed request.
                raise SuspiciousOperation('Cookie missing')
        else:
            verify_sso_jwt(sso_jwt_data=sso_jwt_data, user=user)

        # Also check 'HTTP_AUTHORIZATION', but only the username ;)
        try:
            authorization = request.META[settings.YNH_BASIC_AUTH_HEADER_KEY]
        except KeyError:
            logger.error('%r missing!', settings.YNH_BASIC_AUTH_HEADER_KEY)
            raise SuspiciousOperation('Missing header')

        scheme, creds = authorization.split(' ', 1)
        if scheme.lower() != 'basic':
            logger.error('%r with %r not supported', settings.YNH_BASIC_AUTH_HEADER_KEY, scheme)
            raise SuspiciousOperation('Header scheme not supported')

        creds = str(base64.b64decode(creds), encoding='utf-8')
        username = creds.split(':', 1)[0]
        if username != user.username:
            logger.error(f'%r mismatch: {username=} is not {user.username}', settings.YNH_BASIC_AUTH_HEADER_KEY)
            raise SuspiciousOperation('Wrong username')

        if not was_authenticated:
            # First request, after login -> update user informations
            logger.info('Remote user "%s" was logged in', user)
            user = update_user_profile(request, user)

            user = call_setup_user(user=user)
            assert isinstance(user, UserModel)

            # persist user in the session
            request.user = user
            auth.login(request, user)
