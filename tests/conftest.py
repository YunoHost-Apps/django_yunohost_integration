"""
    Special pytest init:

        - Build a "local_test" YunoHost installation
        - init Django with this local test installation

    So the pytests will run against this local test installation
"""
import os
import sys
from pathlib import Path

import django

from django_yunohost_integration.local_test import create_local_test


BASE_PATH = Path(__file__).parent.parent

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


def pytest_configure():
    print('Compile YunoHost files...')
    final_home_path = create_local_test(
        django_settings_path=BASE_PATH / 'conf' / 'settings.py',
        destination=BASE_PATH / 'local_test',
        runserver=False,
    )
    print('Local test files created here:')
    print(f'"{final_home_path}"')

    os.chdir(final_home_path)
    final_home_str = str(final_home_path)
    if final_home_str not in sys.path:
        sys.path.insert(0, final_home_str)

    django.setup()
