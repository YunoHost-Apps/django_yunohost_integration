import dataclasses
from pathlib import Path

from django_yunohost_integration.cli_dev import app
from django_yunohost_integration.local_test import create_local_test
from django_yunohost_integration.path_utils import get_project_root


@dataclasses.dataclass
class LocalTestArgs:
    # Path to YunoHost package settings.py file (in "conf" directory)
    setting: Path = get_project_root() / 'conf' / 'settings.py'

    # Destination directory for the local test files
    destination: Path = get_project_root() / 'local_test'

    # Start Django "runserver" after local test file creation?
    runserver: bool = True


@app.command
def local_test(*, args: LocalTestArgs):
    """
    Build a "local_test" YunoHost installation and start the Django dev. server against it.
    """
    create_local_test(
        django_settings_path=args.setting,
        destination=args.destination,
        runserver=args.runserver,
        extra_replacements={'__DEBUG_ENABLED__': 'YES'},
    )
