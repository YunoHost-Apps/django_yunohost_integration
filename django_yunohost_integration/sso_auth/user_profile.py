import logging
from functools import lru_cache

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)


UserModel = get_user_model()


@lru_cache(maxsize=None)
def get_setup_user_func():
    setup_user_func = import_string(settings.YNH_SETUP_USER)
    assert callable(setup_user_func)
    return setup_user_func


def call_setup_user(user):
    """
    Hook for the YunoHost package application to setup a Django user.
    Call function defined in settings.YNH_SETUP_USER

    called via:
        * SSOwatUserBackend after a new user was created
        * SSOwatRemoteUserMiddleware on login request
    """
    old_pk = user.pk

    setup_user_func = get_setup_user_func()
    logger.debug('Call "%s" for user "%s"', settings.YNH_SETUP_USER, user)

    user = setup_user_func(user=user)

    assert isinstance(user, UserModel)
    assert user.pk == old_pk

    return user


def update_user_profile(request, user):
    """
    Update existing user information:
     * Email
     * First / Last name

    Called via:
     * SSOwatUserBackend after a new user was created
     * SSOwatRemoteUserMiddleware on login request
    """
    update_fields = []

    if user.is_authenticated and not user.has_usable_password():
        # Empty password is not valid, so we can't save the model, because of full_clean() call
        logger.info('Set unusable password for user: %s', user)
        user.set_unusable_password()
        update_fields.append('password')

    email = request.META.get('HTTP_EMAIL')
    if email and user.email != email:
        logger.info('Update email: %r -> %r', user.email, email)
        user.email = email
        update_fields.append('email')

    raw_username = request.META.get('HTTP_NAME')
    if raw_username:
        if ' ' in raw_username:
            first_name, last_name = raw_username.split(' ', 1)
        else:
            first_name = ''
            last_name = raw_username

        if user.first_name != first_name:
            logger.info('Update first name: %r -> %r', user.first_name, first_name)
            user.first_name = first_name
            update_fields.append('first_name')

        if user.last_name != last_name:
            logger.info('Update last name: %r -> %r', user.last_name, last_name)
            user.last_name = last_name
            update_fields.append('last_name')

    if update_fields:
        try:
            user.full_clean()
        except ValidationError:
            logger.exception('Can not update user: %s', user)
        else:
            user.save(update_fields=update_fields)

    return user
