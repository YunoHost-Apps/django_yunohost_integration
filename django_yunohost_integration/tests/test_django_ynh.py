import os

import django_example
from axes.models import AccessLog
from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.conf import LazySettings, settings
from django.contrib.auth.models import User
from django.test import override_settings
from django.test.testcases import TestCase
from django.urls.base import reverse

from django_yunohost_integration.test_utils import generate_basic_auth


class DjangoYnhTestCase(HtmlAssertionMixin, TestCase):
    def setUp(self):
        super().setUp()

        # Always start a fresh session:
        self.client = self.client_class()

    def test_settings(self):
        assert isinstance(settings, LazySettings)
        assert settings.configured is True

        # default YunoHost app replacements:

        assert str(settings.DATA_DIR_PATH).endswith('/local_test/opt_yunohost')
        assert str(settings.INSTALL_DIR_PATH).endswith('/local_test/var_www')
        assert str(settings.LOG_FILE).endswith('/local_test/var_log_django_yunohost_integration.log')
        assert settings.PATH_URL == 'app_path'
        assert settings.MEDIA_URL == '/app_path/media/'
        assert settings.STATIC_URL == '/app_path/static/'

        # config_panel.toml settings:

        self.assertEqual(settings.DEBUG_ENABLED, 'NO')
        assert settings.LOG_LEVEL == 'DEBUG'
        assert settings.ADMIN_EMAIL == 'admin-email@test.intranet'
        assert settings.DEFAULT_FROM_EMAIL == 'default-from-email@test.intranet'

        # Normal settings:
        self.assertIs(settings.DEBUG, False)
        assert settings.ROOT_URLCONF == 'urls'
        assert settings.ADMINS == (('The Admin Username', 'admin-email@test.intranet'),)
        assert settings.MANAGERS == (('The Admin Username', 'admin-email@test.intranet'),)
        assert settings.SERVER_EMAIL == 'admin-email@test.intranet'
        assert settings.ALLOWED_HOSTS == [
            '127.0.0.1',  # The real entry
            'testserver',  # Added by Django's setup_test_environment()
        ]

        # Set in tests.conftest.pytest_configure via create_local_test():
        assert settings.EXTRA_REPLACEMENT == 'Just for the unittests ;)'

        # Logging example correct?
        log_filename = settings.LOGGING['handlers']['log_file']['filename']
        assert log_filename.endswith('/local_test/var_log_django_yunohost_integration.log')
        assert settings.LOGGING['loggers']['django_yunohost_integration'] == {
            'handlers': ['console', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        }

    def test_urls(self):
        assert settings.PATH_URL == 'app_path'
        assert settings.ROOT_URLCONF == 'urls'
        assert reverse('admin:index') == '/app_path/admin/'

        response = self.client.get('/', secure=True)
        self.assertRedirects(response, expected_url='/app_path/', fetch_redirect_response=False)

    def test_auth(self):
        # SecurityMiddleware should redirects all non-HTTPS requests to HTTPS:
        assert settings.SECURE_SSL_REDIRECT is True
        response = self.client.get('/app_path/', secure=False)
        self.assertRedirects(
            response,
            status_code=301,  # permanent redirect
            expected_url='https://testserver/app_path/',
            fetch_redirect_response=False,
        )

        with self.assertLogs('django_example') as logs:
            response = self.client.get('/app_path/', secure=True)
            self.assert_html_parts(
                response,
                parts=(
                    f'<h2>YunoHost Django Example Project v{django_example.__version__}</h2>',
                    '<a href="/app_path/admin/">Home</a>',
                    '<p>Log in to see more information</p>',
                    '<tr><td>User:</td><td>AnonymousUser</td></tr>',
                    '<tr><td>META:</td><td></td></tr>',
                ),
            )
        self.assertEqual(logs.output, ['INFO:django_example.views:DebugView request from user: AnonymousUser'])

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_create_unknown_user(self):
        assert User.objects.count() == 0

        self.client.cookies['SSOwAuthUser'] = 'test'

        with self.assertLogs('django_example') as logs:
            response = self.client.get(
                path='/app_path/',
                HTTP_REMOTE_USER='test',
                HTTP_AUTH_USER='test',
                HTTP_AUTHORIZATION='basic dGVzdDp0ZXN0MTIz',
            )

            assert User.objects.count() == 1
            user = User.objects.first()
            assert user.username == 'test'
            assert user.is_active is True
            assert user.is_staff is True  # Set by: 'setup_user.setup_project_user'
            assert user.is_superuser is False

        self.assert_html_parts(
            response,
            parts=(
                f'<h2>YunoHost Django Example Project v{django_example.__version__}</h2>',
                '<a href="/app_path/admin/">Django Admin</a>',
                '<tr><td>User:</td><td>test</td></tr>',
                f'<tr><td>Process ID:</td><td>{os.getpid()}</td></tr>',
            ),
        )
        self.assertEqual(logs.output, ['INFO:django_example.views:DebugView request from user: test'])

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_wrong_auth_user(self):
        assert User.objects.count() == 0
        assert AccessLog.objects.count() == 0

        self.client.cookies['SSOwAuthUser'] = 'test'

        response = self.client.get(
            path='/app_path/',
            HTTP_REMOTE_USER='test',
            HTTP_AUTH_USER='foobar',  # <<< wrong user name
            HTTP_AUTHORIZATION='basic dGVzdDp0ZXN0MTIz',
        )

        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.username == 'test'
        assert user.is_active is True
        assert user.is_staff is True  # Set by: 'setup_user.setup_project_user'
        assert user.is_superuser is False

        assert AccessLog.objects.count() == 1

        assert response.status_code == 403  # Forbidden

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_wrong_cookie(self):
        assert User.objects.count() == 0
        assert AccessLog.objects.count() == 0

        self.client.cookies['SSOwAuthUser'] = 'foobar'  # <<< wrong user name

        response = self.client.get(
            path='/app_path/',
            HTTP_REMOTE_USER='test',
            HTTP_AUTH_USER='test',
            HTTP_AUTHORIZATION='basic dGVzdDp0ZXN0MTIz',
        )

        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.username == 'test'
        assert user.is_active is True
        assert user.is_staff is True  # Set by: 'setup_user.setup_project_user'
        assert user.is_superuser is False

        assert AccessLog.objects.count() == 1

        assert response.status_code == 403  # Forbidden

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_wrong_authorization_user(self):
        assert User.objects.count() == 0
        assert AccessLog.objects.count() == 0

        self.client.cookies['SSOwAuthUser'] = 'test'

        response = self.client.get(
            path='/app_path/',
            HTTP_REMOTE_USER='test',
            HTTP_AUTH_USER='test',
            HTTP_AUTHORIZATION=generate_basic_auth(username='foobar', password='test123'),  # <<< wrong user name
        )

        assert User.objects.count() == 1
        user = User.objects.first()
        assert user.username == 'test'
        assert user.is_active is True
        assert user.is_staff is True  # Set by: 'setup_user.setup_project_user'
        assert user.is_superuser is False

        assert AccessLog.objects.count() == 1

        assert response.status_code == 403  # Forbidden
