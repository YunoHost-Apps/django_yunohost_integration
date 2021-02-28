import base64
import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import RemoteUserMiddleware


try:
    from axes.exceptions import AxesBackendPermissionDenied as SuspiciousOperation  # log to Axes DB models
except ImportError:
    from django.core.exceptions import SuspiciousOperation

from django_yunohost_integration.sso_auth.user_profile import call_setup_user, update_user_profile


logger = logging.getLogger(__name__)


UserModel = get_user_model()


class SSOwatRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Middleware to login a user via HTTP_REMOTE_USER header.
    Use Django Axes if something is wrong.
    Update exising user informations.
    """

    header = 'HTTP_REMOTE_USER'
    force_logout_if_no_header = True

    def process_request(self, request):
        # Keep the information if the user is already logged in
        was_authenticated = request.user.is_authenticated

        super().process_request(request)  # login remote user

        user = request.user

        if not user.is_authenticated:
            logger.debug('Not logged in -> nothing to verify here')
            return

        # Check SSOwat cookie informations:
        try:
            username = request.COOKIES['SSOwAuthUser']
        except KeyError:
            logger.error('SSOwAuthUser cookie missing!')

            if settings.DEBUG:
                # e.g.: local test can't set a Cookie easily
                logger.warning('Ignore error, because settings.DEBUG is on!')
            else:
                # emits a signal indicating user login failed, which is processed by
                # axes.signals.log_user_login_failed which logs and flags the failed request.
                raise SuspiciousOperation('Cookie missing')
        else:
            logger.info('SSOwat username from cookies: %r', username)
            if username != user.username:
                raise SuspiciousOperation('Wrong username')

        # Compare with HTTP_AUTH_USER
        try:
            username = request.META['HTTP_AUTH_USER']
        except KeyError:
            logger.error('HTTP_AUTH_USER missing!')
            raise SuspiciousOperation('No HTTP_AUTH_USER')

        if username != user.username:
            raise SuspiciousOperation('Wrong HTTP_AUTH_USER username')

        # Also check 'HTTP_AUTHORIZATION', but only the username ;)
        try:
            authorization = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            logger.error('HTTP_AUTHORIZATION missing!')
            raise SuspiciousOperation('No HTTP_AUTHORIZATION')

        scheme, creds = authorization.split(' ', 1)
        if scheme.lower() != 'basic':
            logger.error('HTTP_AUTHORIZATION with %r not supported', scheme)
            raise SuspiciousOperation('HTTP_AUTHORIZATION scheme not supported')

        creds = str(base64.b64decode(creds), encoding='utf-8')
        username = creds.split(':', 1)[0]
        if username != user.username:
            raise SuspiciousOperation('Wrong HTTP_AUTHORIZATION username')

        if not was_authenticated:
            # First request, after login -> update user informations
            logger.info('Remote user "%s" was logged in', user)
            user = update_user_profile(request, user)

            user = call_setup_user(user=user)
            assert isinstance(user, UserModel)

            # persist user in the session
            request.user = user
            auth.login(request, user)
