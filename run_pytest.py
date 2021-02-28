"""
    Run pytest against local test creation
"""

from pathlib import Path


try:
    from django_yunohost_integration.pytest_helper import run_pytest
except ImportError as err:
    raise ImportError('Did you forget to activate a virtual environment?') from err


BASE_PATH = Path(__file__).parent


def main():
    run_pytest(
        django_settings_path=BASE_PATH / 'conf' / 'settings.py',
        destination=BASE_PATH / 'local_test',
    )


if __name__ == '__main__':
    main()
