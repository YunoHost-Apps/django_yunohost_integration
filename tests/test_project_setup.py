import filecmp
import os
import shutil
import subprocess
from pathlib import Path

import dev_shell
from django_tools.unittest_utils.assertments import assert_is_file

import django_yunohost_integration


PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent


def assert_file_contains_string(file_path, string):
    with file_path.open('r') as f:
        for line in f:
            if string in line:
                return
    raise AssertionError(f'File {file_path} does not contain {string!r} !')


def test_version(package_root=None, version=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    if version is None:
        version = django_yunohost_integration.__version__

    if 'dev' not in version and 'rc' not in version:
        version_string = f'v{version}'

        assert_file_contains_string(file_path=Path(package_root, 'README.md'), string=version_string)

    assert_file_contains_string(file_path=Path(package_root, 'pyproject.toml'), string=f'version = "{version}"')


def test_poetry_check(package_root=None):
    if package_root is None:
        package_root = PACKAGE_ROOT

    poerty_bin = shutil.which('poetry')

    output = subprocess.check_output(
        [poerty_bin, 'check'],
        text=True,
        env=os.environ,
        stderr=subprocess.STDOUT,
        cwd=str(package_root),
    )
    print(output)
    assert output == 'All set!\n'


def test_source_file_is_up2date():
    own_bootstrap_file = PACKAGE_ROOT / 'devshell.py'
    assert_is_file(own_bootstrap_file)

    bootstrap_source_file = Path(dev_shell.__file__).parent / 'bootstrap-source.py'
    assert_is_file(bootstrap_source_file)

    are_the_same = filecmp.cmp(bootstrap_source_file, own_bootstrap_file, shallow=False)
    if not are_the_same:
        shutil.copyfile(src=bootstrap_source_file, dst=own_bootstrap_file, follow_symlinks=False)
        raise AssertionError(f'Bootstrap source "{own_bootstrap_file}" updated!')
