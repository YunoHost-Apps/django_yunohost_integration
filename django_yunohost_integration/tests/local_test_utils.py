import os
import sys
from pathlib import Path

from bx_py_utils.path import assert_is_file
from django.core.management import execute_from_command_line

import django_yunohost_integration
from django_yunohost_integration.local_test import CreateResults, create_local_test


def run_local_test_manage():
    PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent
    assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

    result: CreateResults = create_local_test(
        django_settings_path=PACKAGE_ROOT / 'conf' / 'settings.py',
        destination=PACKAGE_ROOT / 'local_test',
        runserver=False,
        extra_replacements={
            '__DEBUG_ENABLED__': '0',
            '__EXTRA_REPLACEMENT__': 'Just for the unittests ;)',
        },
    )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    # Add ".../local_test/opt_yunohost/" to sys.path, so that "settings" is importable:
    final_home_str = str(result.final_path)
    if final_home_str not in sys.path:
        sys.path.insert(0, final_home_str)

    execute_from_command_line(sys.argv)
