import os
import sys
from pathlib import Path

from django_yunohost_integration.local_test import create_local_test
from django_yunohost_integration.path_utils import assert_is_dir, assert_is_file


def run_pytest(django_settings_path, destination):
    """
    1. Generate "local test installation"
    2. Run pytest against generated sources
    """
    assert_is_file(django_settings_path)

    conf_path = django_settings_path.parent
    base_path = conf_path.parent
    test_path = Path(base_path / 'tests')

    assert_is_dir(test_path)

    final_home_path = create_local_test(
        django_settings_path=django_settings_path,
        destination=destination,
        runserver=False,
    )
    django_settings_name = django_settings_path.stem
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_name
    print(f'DJANGO_SETTINGS_MODULE={django_settings_name}')

    sys.path.insert(0, str(final_home_path))

    import pytest

    # collect only project tests and pass existing pytest arguments:
    sys.argv = [__file__, str(test_path)] + sys.argv[1:]

    raise SystemExit(pytest.console_main())
