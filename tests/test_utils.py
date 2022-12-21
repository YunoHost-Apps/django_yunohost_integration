import requests_mock
from bx_py_utils.environ import OverrideEnviron
from django.test import SimpleTestCase
from packaging.version import Version

from django_yunohost_integration.test_utils import (
    assert_project_version,
    generate_basic_auth,
    get_github_version_tag,
)


class TestUtilsTestCase(SimpleTestCase):
    def test_generate_basic_auth(self):
        assert generate_basic_auth(username='test', password='test123') == 'basic dGVzdDp0ZXN0MTIz'

    def test_get_github_version_tag(self):
        with OverrideEnviron(GITHUB_ACTION=None):
            with requests_mock.Mocker() as m:
                m.get(
                    'https://api.github.com/repos/YunoHost-Apps/django_yunohost_integration/tags',
                    json=[{'name': 'v1.2.3'}],
                )
                ver_obj = get_github_version_tag(
                    github_project_url=(
                        'https://github.com/YunoHost-Apps/django_yunohost_integration'
                    )
                )
            assert ver_obj == Version('1.2.3')

            ###########################################################################

            with self.assertRaisesMessage(
                AssertionError, "No Github Project url: 'http/foo.tld/bar'"
            ):
                get_github_version_tag(github_project_url='http/foo.tld/bar')

            ###########################################################################

            with requests_mock.Mocker() as m, self.assertRaisesMessage(
                AssertionError,
                (
                    'No version found from github tags:'
                    ' https://api.github.com/repos/YunoHost-Apps/django_yunohost_integration'
                    ' (check: https://github.com/YunoHost-Apps/django_yunohost_integration)'
                ),
            ):
                m.get(
                    'https://api.github.com/repos/YunoHost-Apps/django_yunohost_integration/tags',
                    json=[],
                )

                get_github_version_tag(
                    github_project_url=(
                        'https://github.com/YunoHost-Apps/django_yunohost_integration'
                    )
                )

    def test_assert_project_version(self):
        with OverrideEnviron(GITHUB_ACTION=None):
            with requests_mock.Mocker() as m:
                m.get(
                    'https://api.github.com/repos/YunoHost-Apps/django_yunohost_integration/tags',
                    json=[{'name': 'v1.2.3'}],
                )
                assert_project_version(
                    current_version='v1.2.3',
                    github_project_url=(
                        'https://github.com/YunoHost-Apps/django_yunohost_integration'
                    ),
                )

            ###########################################################################

            with requests_mock.Mocker() as m, self.assertRaisesMessage(
                AssertionError,
                (
                    'Current version from'
                    ' https://github.com/YunoHost-Apps/django_yunohost_integration'
                    ' is: 1.2.3 but current package version is: 1.0.0'
                ),
            ):
                m.get(
                    'https://api.github.com/repos/YunoHost-Apps/django_yunohost_integration/tags',
                    json=[{'name': 'v1.2.3'}],
                )

                assert_project_version(
                    current_version='v1.0.0',
                    github_project_url=(
                        'https://github.com/YunoHost-Apps/django_yunohost_integration'
                    ),
                )
