"""
    Build a "local_test" YunoHost installation and start the Django dev. server against it.

    Run via:
        make local-test

    see README for details ;)
"""
from pathlib import Path


try:
    from django_yunohost_integration.local_test import create_local_test
except ImportError as err:
    raise ImportError('Did you forget to activate a virtual environment?') from err

BASE_PATH = Path(__file__).parent


def main():
    create_local_test(
        django_settings_path=BASE_PATH / 'conf' / 'settings.py',
        destination=BASE_PATH / 'local_test',
        runserver=True,
    )


if __name__ == '__main__':
    main()
