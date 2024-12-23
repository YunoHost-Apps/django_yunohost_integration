import jwt
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.test import SimpleTestCase

from django_yunohost_integration.yunohost.ynh_jwt import verify_sso_jwt


def create_jwt(*, username: str) -> str:
    return jwt.encode(
        payload={'user': username},
        key='ssowat-cookie-secret',
        algorithm='HS256',
    )


class YunohostJwtTestCase(SimpleTestCase):

    def test_happy_path(self):
        with self.assertLogs('django_yunohost_integration') as cm:
            verify_sso_jwt(
                sso_jwt_data=create_jwt(username='Foo Bar'),
                user=User(username='Foo Bar'),
            )
        self.assertEqual(
            cm.output, ["INFO:django_yunohost_integration.yunohost.ynh_jwt:JWT username 'Foo Bar' is valid"]
        )

    def test_wrong_username(self):
        with (
            self.assertLogs('django_yunohost_integration') as cm,
            self.assertRaisesMessage(SuspiciousOperation, 'Wrong username'),
        ):
            verify_sso_jwt(
                sso_jwt_data=create_jwt(username='Bar'),
                user=User(username='Foo'),
            )
        self.assertEqual(
            cm.output,
            [
                "ERROR:django_yunohost_integration.yunohost.ynh_jwt:"
                "Mismatch: jwt_username='Bar' is not user.username='Foo'"
            ],
        )
