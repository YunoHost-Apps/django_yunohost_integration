from django.core.checks import Error
from django.core.checks.registry import CheckRegistry, registry
from django.test.testcases import TestCase

from django_yunohost_integration.system_checks import validate_settings_emails


class SystemChecksTestCase(TestCase):
    def test_is_registered(self):
        assert isinstance(registry, CheckRegistry)
        self.assertIn(validate_settings_emails, registry.registered_checks)

    def _validate_emails(self, expected_errors):
        errors = validate_settings_emails(app_configs=None)
        self.assertEqual(errors, expected_errors)

    def test_validate_emails(self):

        self._validate_emails(expected_errors=[])

        with self.settings(FOO_BAR_EMAIL='invalid email!'):
            self._validate_emails(
                expected_errors=[
                    Error(
                        "FOO_BAR_EMAIL 'invalid email!' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.E001',
                    )
                ]
            )

        with self.settings(ADMINS=[('foo', 'no valid email!')]):
            self._validate_emails(
                expected_errors=[
                    Error(
                        "ADMINS (foo) 'no valid email!' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.E001',
                    )
                ]
            )

        with self.settings(MANAGERS=[('bar', 'foo @ bar')]):
            self._validate_emails(
                expected_errors=[
                    Error(
                        "MANAGERS (bar) 'foo @ bar' is not valid!",
                        hint='Check your config panel email values!',
                        id='django_yunohost_integration.E001',
                    )
                ]
            )
