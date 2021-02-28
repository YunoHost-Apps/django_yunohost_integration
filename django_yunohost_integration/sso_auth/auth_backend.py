"""
    remote user authentication backend

    Note: SSOwat/nginx add authentication headers:

        'HTTP_AUTHORIZATION': 'Basic XXXXXXXXXXXXXXXX='
        'HTTP_AUTH_USER': 'username'
        'HTTP_REMOTE_USER': 'username'

    Basic auth contains "{username}:{plaintext-password}"

    and we get SSOwat cookies like:

         'HTTP_COOKIE': 'SSOwAuthUser=username; '
                        'SSOwAuthHash=593876aa66...99e69f88af1e; '
                        'SSOwAuthExpire=1609227697.998; '

    * Login a user via HTTP_REMOTE_USER header, but check also username in:
        * SSOwAuthUser
        * HTTP_AUTH_USER
        * HTTP_AUTHORIZATION (Basic auth)
    * Create new users
    * Update Email, First / Last name for existing users
"""

import logging

from django.contrib.auth.backends import RemoteUserBackend

from django_yunohost_integration.sso_auth.user_profile import call_setup_user, update_user_profile


logger = logging.getLogger(__name__)


class SSOwatUserBackend(RemoteUserBackend):
    """
    Authentication backend via SSO/nginx header
    """

    create_unknown_user = True

    def authenticate(self, request, remote_user):
        logger.info('Remote user authenticate: %r', remote_user)
        return super().authenticate(request, remote_user)

    def configure_user(self, request, user):
        """
        Configure a new user after creation and return the updated user.
        """
        logger.warning('Configure user %s', user)

        user = update_user_profile(request, user)
        user = call_setup_user(user=user)

        return user

    def user_can_authenticate(self, user):
        logger.warning('Remote user login: %s', user)
        assert not user.is_anonymous
        return True
