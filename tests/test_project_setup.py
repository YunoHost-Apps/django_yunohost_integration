import filecmp
import shutil
from pathlib import Path

import dev_shell
from django_tools.unittest_utils.assertments import assert_is_file
from django_tools.unittest_utils.project_setup import check_editor_config
from poetry_publish.tests.test_project_setup import assert_file_contains_string
from poetry_publish.tests.test_project_setup import test_poetry_check as assert_poetry_check

import django_yunohost_integration
from django_yunohost_integration.test_utils import assert_project_version


PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent


def test_version(package_root=None, version=None, github_project_url=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    if version is None:
        version = django_yunohost_integration.__version__

    if github_project_url is None:
        github_project_url = 'https://github.com/YunoHost-Apps/django_yunohost_integration'

    # Check that current version is the last version from Github tags:
    assert_project_version(current_version=version, github_project_url=github_project_url)

    assert_file_contains_string(
        file_path=Path(package_root, 'README.md'),
        string=f'v{version}',
    )

    assert_file_contains_string(
        file_path=Path(package_root, 'pyproject.toml'),
        string=f'version = "{version}"',
    )


def test_poetry_check():
    """
    Test 'poetry check' output.
    """
    assert_poetry_check(package_root=PACKAGE_ROOT)


def test_source_file_is_up2date():
    own_bootstrap_file = PACKAGE_ROOT / 'devshell.py'
    assert_is_file(own_bootstrap_file)

    bootstrap_source_file = Path(dev_shell.__file__).parent / 'bootstrap-source.py'
    assert_is_file(bootstrap_source_file)

    are_the_same = filecmp.cmp(bootstrap_source_file, own_bootstrap_file, shallow=False)
    if not are_the_same:
        shutil.copyfile(src=bootstrap_source_file, dst=own_bootstrap_file, follow_symlinks=False)
        raise AssertionError(f'Bootstrap source "{own_bootstrap_file}" updated!')


def test_check_editor_config():
    check_editor_config(package_root=PACKAGE_ROOT)
