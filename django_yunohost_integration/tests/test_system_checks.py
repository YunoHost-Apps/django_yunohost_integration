import tempfile
from unittest.mock import patch

from django.core.checks import Warning
from django.core.checks.registry import CheckRegistry, registry
from django.test.testcases import SimpleTestCase

from django_yunohost_integration import yunohost_utils
from django_yunohost_integration.system_checks import (
    check_ynh_current_host,
    validate_log_level,
    validate_settings_emails,
)
from django_yunohost_integration.yunohost_utils import get_ssowat_domain


class SystemChecksTestCase(SimpleTestCase):
    def test_is_registered(self):
        assert isinstance(registry, CheckRegistry)
        self.assertIn(validate_settings_emails, registry.registered_checks)
        self.assertIn(validate_log_level, registry.registered_checks)

    def _validate_emails(self, expected_errors):
        errors = validate_settings_emails(app_configs=None)
        self.assertEqual(errors, expected_errors)

    def test_validate_emails(self):
        self._validate_emails(expected_errors=[])

        with self.settings(FOO_BAR_EMAIL='invalid email!'):
            self._validate_emails(
                expected_errors=[
                    Warning(
                        "FOO_BAR_EMAIL 'invalid email!' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.W001',
                    )
                ]
            )

        with self.settings(ADMINS=[('foo', 'no valid email!')]):
            self._validate_emails(
                expected_errors=[
                    Warning(
                        "ADMINS (foo) 'no valid email!' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.W001',
                    )
                ]
            )

        with self.settings(MANAGERS=[('bar', 'foo @ bar')]):
            self._validate_emails(
                expected_errors=[
                    Warning(
                        "MANAGERS (bar) 'foo @ bar' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.W001',
                    )
                ]
            )

    def _validate_log_level(self, expected_errors):
        errors = validate_log_level(app_configs=None)
        self.assertEqual(errors, expected_errors)

    def test_validate_log_level(self):
        self._validate_log_level(expected_errors=[])
        with self.settings(LOG_LEVEL='foobar'):
            self._validate_log_level(
                expected_errors=[
                    Warning(
                        "'foobar' is not a valid log level name!",
                        hint='Check your config panel values!',
                        id='django_yunohost_integration.W002',
                    )
                ]
            )

    def test_check_ynh_current_host_setting(self):
        with tempfile.NamedTemporaryFile(prefix='current_host') as tmp:
            with patch.object(yunohost_utils, 'YNH_CURRENT_HOST', tmp.name):
                errors = check_ynh_current_host(app_configs=None)
                self.assertEqual(
                    errors,
                    [
                        Warning(
                            msg=f"'{tmp.name}' is empty",
                            id='django_yunohost_integration.W003',
                        )
                    ],
                )

                tmp.write(b'ynh.test.tld')
                tmp.flush()
                self.assertEqual(get_ssowat_domain(), 'ynh.test.tld')

                errors = check_ynh_current_host(app_configs=None)
                self.assertEqual(errors, [])

                tmp.seek(0)
                tmp.write(b'This is no domain!')
                tmp.flush()

                errors = check_ynh_current_host(app_configs=None)
                self.assertEqual(
                    errors,
                    [
                        Warning(
                            msg="'This is no domain!' is invalid",
                            id='django_yunohost_integration.W003',
                        )
                    ],
                )

        with patch.object(yunohost_utils, 'YNH_CURRENT_HOST', '/file/path/not/exists'):
            errors = check_ynh_current_host(app_configs=None)
            self.assertEqual(
                errors,
                [
                    Warning(
                        msg=("No such file: '/file/path/not/exists'"),
                        id='django_yunohost_integration.W003',
                    )
                ],
            )
