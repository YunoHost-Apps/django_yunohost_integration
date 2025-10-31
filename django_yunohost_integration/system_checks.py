from django.conf import settings
from django.core.checks import Warning, register
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


VALID_LOG_LEVEL_NAMES = (
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
)


@register()
def validate_log_level(app_configs, **kwargs):
    errors = []
    if settings.LOG_LEVEL not in VALID_LOG_LEVEL_NAMES:
        errors.append(
            Warning(
                f'{settings.LOG_LEVEL!r} is not a valid log level name!',
                hint='Check your config panel values!',
                id='django_yunohost_integration.W002',
            )
        )
    return errors


def validate_email(errors, email, settings_key):
    try:
        EmailValidator()(email)
    except ValidationError:
        errors.append(
            Warning(
                f'{settings_key} {email!r} is not valid!',
                hint='Check your config panel email values!',
                id='django_yunohost_integration.W001',
            )
        )


@register()
def validate_settings_emails(app_configs, **kwargs):
    errors = []

    assert settings.configured

    for key in dir(settings):
        if key.startswith('_'):
            continue

        if key.endswith('_EMAIL'):
            value = getattr(settings, key)
            if value:
                validate_email(errors, email=value, settings_key=key)

    for user_name, email in settings.ADMINS:
        validate_email(errors, email=email, settings_key=f'ADMINS ({user_name})')

    for user_name, email in settings.MANAGERS:
        validate_email(errors, email=email, settings_key=f'MANAGERS ({user_name})')

    return errors



