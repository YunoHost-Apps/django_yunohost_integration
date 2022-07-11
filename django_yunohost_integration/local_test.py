"""
    Create a YunoHost package local test
"""
import argparse
import inspect
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from django_yunohost_integration.path_utils import assert_is_dir, assert_is_file
from django_yunohost_integration.test_utils import generate_basic_auth


def verbose_check_call(command, verbose=True, extra_env=None, **kwargs):
    """ 'verbose' version of subprocess.check_call() """
    if verbose:
        print('_' * 100)
        msg = f'Call: {command!r}'
        verbose_kwargs = ', '.join(f'{k}={v!r}' for k, v in sorted(kwargs.items()))
        if verbose_kwargs:
            msg += f' (kwargs: {verbose_kwargs})'
        print(f'{msg}\n', flush=True)

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    if extra_env is not None:
        assert isinstance(extra_env, dict)
        env.update(extra_env)

    popenargs = shlex.split(command)
    subprocess.check_call(popenargs, universal_newlines=True, env=env, **kwargs)


def call_manage_py(final_home_path, args, extra_env=None):
    assert_is_file(final_home_path / 'manage.py')
    verbose_check_call(
        command=f'{sys.executable} manage.py {args}',
        extra_env=extra_env,
        cwd=final_home_path,
    )


def copy_patch(src_file, replaces, final_home_path):
    dst_file = final_home_path / src_file.name
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


def create_local_test(django_settings_path, destination, runserver=False):
    django_settings_path = django_settings_path.resolve()
    assert_is_file(django_settings_path)

    django_settings_name = django_settings_path.stem
    conf_path = django_settings_path.parent
    root_path = conf_path.parent

    # Get the YunoHost app name from manifest:
    manifest_path = root_path / 'manifest.json'
    print(f'Read YunoHost App manifest from: "{manifest_path}"')
    if not manifest_path.is_file():
        # e.g.: self test run ;)
        print(f'WARNING: File not found: "{manifest_path}"')
        project_name = conf_path.parent.name
        print(f'Fall back to root directory name as App id: "{project_name}"')
    else:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
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

    final_home_path = destination / 'opt_yunohost'
    final_www_path = destination / 'var_www'
    log_file = destination / f'var_log_{project_name}.log'

    REPLACES = {
        '__FINAL_HOME_PATH__': str(final_home_path),
        '__FINAL_WWW_PATH__': str(final_www_path),
        '__LOG_FILE__': str(log_file),
        '__PATH_URL__': 'app_path',
        '__DOMAIN__': '127.0.0.1',
        'django.db.backends.postgresql': 'django.db.backends.sqlite3',
        "'NAME': '__APP__',": f"'NAME': '{destination / 'test_db.sqlite'}',",
        'django_redis.cache.RedisCache': 'django.core.cache.backends.dummy.DummyCache',
        # Just use the default logging setup from django_yunohost_integration project:
        'LOGGING = {': 'HACKED_DEACTIVATED_LOGGING = {',
    }

    for p in (final_home_path, final_www_path):
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
        copy_patch(src_file=src_file, replaces=REPLACES, final_home_path=final_home_path)

    local_settings_path = final_home_path / 'local_settings.py'
    local_settings_path.write_text(inspect.cleandoc('''
        # Only for local test run

        import os


        if os.environ.get('ENV_TYPE', None) == 'local':
            print(f'Activate settings overwrite by {__file__}')
            DEBUG = True
            SECURE_SSL_REDIRECT = False  # Don't redirect http to https
            SERVE_FILES = True  # May used in urls.py
            AUTH_PASSWORD_VALIDATORS = []  # accept all passwords
            ALLOWED_HOSTS = ["*"]  # Allow access from "everywhere"
            CACHES = {  # Setup a working cache, without Redis ;)
                'default': {
                    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                    'LOCATION': 'unique-snowflake',
                },
            }
    '''))

    # call "local_test/manage.py" via subprocess:
    call_manage_py(final_home_path, 'check --deploy')
    if runserver:
        call_manage_py(final_home_path, 'migrate --no-input')
        call_manage_py(final_home_path, 'collectstatic --no-input')
        call_manage_py(final_home_path, 'create_superuser --username="test"')

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
                final_home_path,
                'runserver',
                extra_env={'ENV_TYPE': 'local'}  # Activate local_settings.py overwrites
            )
        except KeyboardInterrupt:
            print('\nBye ;)')

    return final_home_path


def cli():
    parser = argparse.ArgumentParser(description='Generate a YunoHost package local test')

    parser.add_argument(
        '--django_settings_path',
        action='store',
        metavar='path',
        help='Path to YunoHost package settings.py file (in "conf" directory)',
    )
    parser.add_argument(
        '--destination',
        action='store',
        metavar='path',
        help='Destination directory for the local test files',
    )
    parser.add_argument(
        '--runserver',
        action='store',
        type=bool,
        default=False,
        help='Start Django "runserver" after local test file creation?',
    )
    args = parser.parse_args()

    create_local_test(
        django_settings_path=Path(args.django_settings_path),
        destination=Path(args.destination),
        runserver=args.runserver,
    )


if __name__ == '__main__':
    cli()
