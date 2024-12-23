import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import SuspiciousOperation


try:
    # https://pypi.org/project/PyJWT/
    # https://github.com/jpadilla/pyjwt
    import jwt
except ImportError as err:
    raise ImportError('Please install the PyJWT package') from err


logger = logging.getLogger(__name__)

UserModel = get_user_model()


def verify_sso_jwt(*, sso_jwt_data: str, user: AbstractUser) -> None:
    assert isinstance(user, UserModel), f'Invalid user type: {type(user)}'

    data = jwt.decode(
        jwt=sso_jwt_data,
        algorithms=['HS256'],
        # So activate 'verify_signature', we need the key.
        # It's the content of /etc/yunohost/.ssowat_cookie_secret
        # But we can't read it, because of file permissions.
        key='',
        options={
            'verify_signature': False,  # No key -> no signature verification
            'require': ['user'],
        },
    )
    jwt_username = data['user']
    if jwt_username != user.username:
        logger.error(f'Mismatch: {jwt_username=} is not {user.username=}')
        raise SuspiciousOperation('Wrong username')
    logger.info('JWT username %r is valid', jwt_username)
