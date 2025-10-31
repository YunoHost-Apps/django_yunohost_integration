
from django.core.checks import Warning
from django.core.checks.registry import CheckRegistry, registry
from django.test.testcases import SimpleTestCase

from django_yunohost_integration.system_checks import (
    validate_log_level,
    validate_settings_emails,
)


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
