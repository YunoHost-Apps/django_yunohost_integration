"""
    Create a YunoHost package local test
"""

import dataclasses
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import tomllib  # New in Python 3.11
except ImportError:
    import tomli as tomllib

from cli_base.cli_tools.subprocess_utils import verbose_check_call
from django_tools.unittest_utils.assertments import assert_is_dir, assert_is_file

import django_yunohost_integration
from django_yunohost_integration.test_utils import generate_basic_auth


BASE_PATH = Path(django_yunohost_integration.__file__).parent


def call_manage_py(data_dir_path, *args, extra_env=None):
    """
    call "local_test/manage.py" via subprocess
    """
    assert_is_file(data_dir_path / 'manage.py')
    verbose_check_call(
        sys.executable,
        'manage.py',
        *args,
        extra_env=extra_env,
        cwd=data_dir_path,
    )


def copy_patch(src_file, replaces, data_dir_path):
    dst_file = data_dir_path / src_file.name
    print(f'{src_file} -> {dst_file}')

    with src_file.open('r') as f:
        content = f.read()

    if replaces:
        for old, new in replaces.items():
            if old in content:
                print(f' * Replace "{old}" -> "{new}"')
                content = content.replace(old, new)

    with dst_file.open('w') as f:
        f.write(content)


@dataclasses.dataclass
class CreateResults:
    data_dir_path: Path
    django_settings_name: str


def create_local_test(
    django_settings_path: Path,
    destination: Path,
    runserver: bool = False,
    extra_replacements: Optional[dict] = None,
) -> CreateResults:
    django_settings_path = django_settings_path.resolve()
    assert_is_file(django_settings_path)

    django_settings_name = django_settings_path.stem
    conf_path = django_settings_path.parent
    root_path = conf_path.parent

    # Get the YunoHost app name from manifest:
    manifest_path = root_path / 'manifest.toml'
    print(f'Read YunoHost App manifest from: "{manifest_path}"')
    if not manifest_path.is_file():
        # e.g.: self test run ;)
        print(f'WARNING: File not found: "{manifest_path}"')
        project_name = conf_path.parent.name
        print(f'Fall back to root directory name as App id: "{project_name}"')
    else:
        manifest = tomllib.loads(manifest_path.read_text(encoding='utf-8'))
        project_name = manifest['id']  # same as: "app=$YNH_APP_INSTANCE_NAME" in YunoHost scripts

    print(f'YunoHost App id: "{project_name}"')

    # Check if App "id" and parent directory seems to match:
    yunohost_package_name = f'{project_name}_ynh'
    if yunohost_package_name != root_path.name:
        print(
            f'WARNING: App id "{project_name}"'
            f' and project root directory name "{conf_path.parent.name}"'
            f' does not match the default name scheme: "{yunohost_package_name}"'
        )

    assert isinstance(destination, Path)
    destination = destination.resolve()
    if not destination.is_dir():
        destination.mkdir(parents=False)

    assert_is_dir(destination)

    data_dir_path = destination / 'opt_yunohost'
    install_dir_path = destination / 'var_www'
    log_file = destination / f'var_log_{project_name}.log'

    REPLACES = {
        '__LOG_FILE__': str(log_file),
        '__APP__': 'app_name',
        '__PATH__': 'app_path',
        '__DOMAIN__': '127.0.0.1',
        'django.db.backends.postgresql': 'django.db.backends.sqlite3',
        '__DB_NAME__': str(destination / 'test_db.sqlite'),
        '__DB_USER__': 'test_db_user',
        '__DB_PWD__': 'test_db_pwd',
        'django_redis.cache.RedisCache': 'django.core.cache.backends.dummy.DummyCache',
        "'syslog'": "'console'",  # Log to console for local test
        #
        # config_panel.toml settings:
        '__DEBUG_ENABLED__': 'YES',
        '__LOG_LEVEL__': 'DEBUG',
        '__ADMIN__': 'The Admin Username',
        '__DEFAULT_FROM_EMAIL__': 'default-from-email@test.intranet',
        #
        # New variable names, for "ynh_add_config" usage:
        '__DATA_DIR__': str(data_dir_path),  # e.g.: /home/yunohost.app/$app/
        '__INSTALL_DIR__': str(install_dir_path),  # e.g.: /var/www/$app/
        '__ADMIN_EMAIL__': 'admin-email@test.intranet',
    }
    if extra_replacements:
        REPLACES.update(extra_replacements)

    for p in (data_dir_path, install_dir_path):
        if p.is_dir():
            print(f'Already exists: "{p}", ok.')
        else:
            p.mkdir(parents=True, exist_ok=True)

    log_file.touch(exist_ok=True)

    # Check that there are some needed files:
    assert_is_file(conf_path / 'manage.py')
    assert_is_file(conf_path / 'settings.py')
    assert_is_file(conf_path / 'urls.py')

    for src_file in conf_path.glob('*.py'):
        copy_patch(src_file=src_file, replaces=REPLACES, data_dir_path=data_dir_path)

    local_settings_path = data_dir_path / 'local_settings.py'
    local_settings_source = Path(BASE_PATH / 'local_settings_source.py')
    local_settings = f'# source file: {local_settings_source}\n'
    local_settings += local_settings_source.read_text()
    local_settings_path.write_text(local_settings)

    if runserver:
        call_manage_py(data_dir_path, 'migrate', '--no-input')
        call_manage_py(data_dir_path, 'collectstatic', '--no-input')
        call_manage_py(data_dir_path, 'create_superuser', '--username="test"')

        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_name

        # All environment variables are passed to Django's "runnserver" ;)
        # "Simulate" SSOwat authentication, by set "http headers"
        # Still missing is the 'SSOwAuthUser' cookie,
        # but this is ignored, if settings.DEBUG=True ;)
        os.environ['HTTP_AUTH_USER'] = 'test'
        os.environ['HTTP_REMOTE_USER'] = 'test'

        os.environ['HTTP_AUTHORIZATION'] = generate_basic_auth(username='test', password='test123')

        try:
            call_manage_py(
                data_dir_path, 'runserver', extra_env={'ENV_TYPE': 'local'}  # Activate local_settings.py overwrites
            )
        except KeyboardInterrupt:
            print('\nBye ;)')
    else:
        print('\n')

    return CreateResults(
        data_dir_path=data_dir_path,
        django_settings_name=django_settings_name,
    )
