from django.conf import settings
from django.core.checks import Error, register
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


def validate_email(errors, email, settings_key):
    try:
        EmailValidator()(email)
    except ValidationError:
        errors.append(
            Error(
                f'{settings_key} {email!r} is not valid!',
                hint='Check your config panel email values!',
                id='django_yunohost_integration.E001',
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
