# django_yunohost_integration

[![tests](https://github.com/YunoHost-Apps/django_yunohost_integration/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/YunoHost-Apps/django_yunohost_integration/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/YunoHost-Apps/django_yunohost_integration/branch/main/graph/badge.svg)](https://app.codecov.io/github/YunoHost-Apps/django_yunohost_integration)
[![django_yunohost_integration @ PyPi](https://img.shields.io/pypi/v/django_yunohost_integration?label=django_yunohost_integration%20%40%20PyPi)](https://pypi.org/project/django_yunohost_integration/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django_yunohost_integration)](https://github.com/YunoHost-Apps/django_yunohost_integration/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/django_yunohost_integration)](https://github.com/YunoHost-Apps/django_yunohost_integration/blob/main/LICENSE)


Python package [django_yunohost_integration](https://pypi.org/project/django_yunohost_integration/) with helpers for integrate a Django project as YunoHost package.

A example usage of this package is here:

* https://github.com/YunoHost-Apps/django_example_ynh

Pull requests welcome ;)


These projects used `django_yunohost_integration`:

* https://github.com/YunoHost-Apps/pyinventory_ynh
* https://github.com/YunoHost-Apps/django-for-runners_ynh
* https://github.com/YunoHost-Apps/django-fmd_ynh


## Features

* SSOwat integration (see below)
* Helper to create first super user for `scripts/install`
* Run Django development server with a local generated YunoHost package installation (called `local_test`)
* Helper to run `test` against `local_test` "installation"


### SSO authentication

[SSOwat](https://github.com/YunoHost/SSOwat) is fully supported:

* First user (`$YNH_APP_ARG_ADMIN`) will be created as Django's super user
* All new users will be created as normal users
* Login via SSO is fully supported
* User Email, First / Last name will be updated from SSO data


### usage

To create/update the first user in `install`/`upgrade`, e.g.:

```bash
./manage.py create_superuser --username="$admin" --email="$admin_mail"
```
This Create/update Django superuser and set a unusable password.
A password is not needed, because auth done via SSOwat ;)

Main parts in `settings.py`:
```python
from pathlib import Path as __Path

from django_yunohost_integration.base_settings import *  # noqa
from django_yunohost_integration.secret_key import get_or_create_secret as __get_or_create_secret


DEBUG = bool(int('__DEBUG_ENABLED__'))  # Set via config_panel.toml

# -----------------------------------------------------------------------------

DATA_DIR_PATH = __Path('__DATA_DIR__')  # /home/yunohost.app/$app
assert DATA_DIR_PATH.is_dir(), f'Directory not exists: {DATA_DIR_PATH}'

INSTALL_DIR_PATH = __Path('__INSTALL_DIR__')  # /var/www/$app
assert INSTALL_DIR_PATH.is_dir(), f'Directory not exists: {INSTALL_DIR_PATH}'

LOG_FILE = __Path('__LOG_FILE__')  # /var/log/$app/$app.log
assert LOG_FILE.is_file(), f'File not exists: {LOG_FILE}'

PATH_URL = '__PATH_URL__'  # $YNH_APP_ARG_PATH
PATH_URL = PATH_URL.strip('/')

# -----------------------------------------------------------------------------

# Function that will be called to finalize a user profile:
YNH_SETUP_USER = 'setup_user.setup_project_user'

SECRET_KEY = __get_or_create_secret(DATA_DIR_PATH / 'secret.txt')  # /home/yunohost.app/$app/secret.txt

# INSTALLED_APPS.append('<insert-your-app-here>')

# -----------------------------------------------------------------------------
```


At least you have to set these settings:
```python
from django_yunohost_integration.base_settings import *  # noqa

INSTALLED_APPS.append('django_yunohost_integration')

MIDDLEWARE.insert(
    MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1,
    # login a user via HTTP_REMOTE_USER header from SSOwat:
    'django_yunohost_integration.sso_auth.auth_middleware.SSOwatRemoteUserMiddleware',
)

# Keep ModelBackend around for per-user permissions and superuser
AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesBackend',  # AxesBackend should be the first backend!
    #
    # Authenticate via SSO and nginx 'HTTP_REMOTE_USER' header:
    'django_yunohost_integration.sso_auth.auth_backend.SSOwatUserBackend',
    #
    # Fallback to normal Django model backend:
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = None
LOGIN_URL = '/yunohost/sso/'
LOGOUT_REDIRECT_URL = '/yunohost/sso/'
# /yunohost/sso/?action=logout

ROOT_URLCONF = 'urls'  # .../conf/urls.py
```


## local test

### Build prerequisites

We install `psycopg2` (a PostgreSQL adapter for the Python) that needs some build prerequisites, e.g.:

```bash
~$ sudo apt install build-essential python3-dev libpq-dev
```

For quicker developing of django_yunohost_integration in the context of YunoHost app,
it's possible to run the Django developer server with the settings
and urls made for YunoHost installation.

e.g.:
```bash
~$ git clone https://github.com/YunoHost-Apps/django_yunohost_integration.git
~$ cd django_yunohost_integration/
~/django_yunohost_integration$ ./dev-cli.py
```

For quicker developing of django_yunohost_integration in the context of YunoHost app,
it's possible to run the Django developer server with the settings
and urls made for YunoHost installation.

e.g.:
```bash
~/django_yunohost_integration$ ./dev-cli.py local-test
```

* SQlite database will be used
* A super user with username `test` and password `test` is created
* The page is available under `http://127.0.0.1:8000/app_path/`


## dev-cli.py usage

[comment]: <> (✂✂✂ auto generated dev help start ✂✂✂)
```
usage: ./dev-cli.py [-h]
                    {check-code-style,coverage,fix-code-style,install,local-test,mypy,nox,pip-audit,publish,test,updat
e,update-test-snapshot-files,version}



╭─ options ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help        show this help message and exit                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ subcommands ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ {check-code-style,coverage,fix-code-style,install,local-test,mypy,nox,pip-audit,publish,test,update,update-test-sn │
│ apshot-files,version}                                                                                              │
│     check-code-style                                                                                               │
│                   Check code style by calling darker + flake8                                                      │
│     coverage      Run tests and show coverage report.                                                              │
│     fix-code-style                                                                                                 │
│                   Fix code style of all django_yunohost_integration source code files via darker                   │
│     install       Install requirements and 'django_yunohost_integration' via pip as editable.                      │
│     local-test    Build a "local_test" YunoHost installation and start the Django dev. server against it.          │
│     mypy          Run Mypy (configured in pyproject.toml)                                                          │
│     nox           Run nox                                                                                          │
│     pip-audit     Run pip-audit check against current requirements files                                           │
│     publish       Build and upload this project to PyPi                                                            │
│     test          Run unittests                                                                                    │
│     update        Update "requirements*.txt" dependencies files                                                    │
│     update-test-snapshot-files                                                                                     │
│                   Update all test snapshot files (by remove and recreate all snapshot files)                       │
│     version       Print version and exit                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated dev help end ✂✂✂)



# Backwards-incompatible changes

## v0.9

Starting with v0.9 we only support YunoHost >= v12.

For this the `auth_middleware` was changed:

* `HTTP_REMOTE_USER` changed `HTTP_YNH_USER`
* `HTTP_AUTH_USER` was removed
* `SSOwAuthUser` changed to JWT token `yunohost.portal`

The YunoHost package nginx config should be set:
```
proxy_set_header Ynh-User $http_ynh_user;
```


# history

[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v0.11.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.10.0...v0.11.0)
  * 2025-03-23 - Apply manageproject updates + update requirements
* [v0.10.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.9.0...v0.10.0)
  * 2025-01-31 - Bugfix publish dev. command
  * 2025-01-31 - pip-tools -> uv + refactor cli
* [v0.9.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.8.1...v0.9.0)
  * 2024-12-23 - fix Python 3.11 install
  * 2024-12-23 - YunoHost >= v12: Use JWT token as validation, too.
  * 2024-12-21 - Project updates
  * 2024-08-29 - Revert "Add install_python.py"
  * 2024-08-27 - Change `--py-version` to optional, positional argument
  * 2024-08-26 - Add install_python.py
* [v0.8.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.8.0...v0.8.1)
  * 2024-08-25 - update assert_is_dir, assert_is_file imports
  * 2024-08-25 - Bugfix codecov.io badge in README
  * 2024-08-25 - Fix CI
  * 2024-08-25 - Update requirements
  * 2024-08-25 - Apply manageprojects updates

<details><summary>Expand older history entries ...</summary>

* [v0.8.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.7.1...v0.8.0)
  * 2024-08-04 - work-a-round for: https://github.com/jazzband/pip-tools/issues/1866
  * 2024-08-04 - Bugfix local "manage.py" helper
  * 2024-08-04 - Update requirements
  * 2024-08-04 - Set Python 3.11 as minimum
  * 2024-08-04 - Add pre-commit scripts
  * 2024-08-04 - safety -> pip-audit
  * 2024-08-04 - 'psycopg2' -> 'psycopg[binary]'
  * 2024-08-04 - Use pre-commit to update history in README
  * 2024-08-04 - Apply manageprojects updates
* [v0.7.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.7.0...v0.7.1)
  * 2024-01-04 - Bugfix create_local_test()
* [v0.7.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.6.0...v0.7.0)
  * 2023-12-22 - Fix publish
  * 2023-12-22 - Update project setup
  * 2023-12-22 - Bugfix: unexpected keyword argument 'created'
  * 2023-08-22 - Update README.md
* [v0.6.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.5.2...v0.6.0)
  * 2023-08-22 - Update requeirements, README and bump version to v0.6.0
  * 2023-08-20 - __PATH_URL__ -> __PATH__
  * 2023-08-20 - update test
  * 2023-08-20 - Replace __DEBUG_ENABLED__ with "YES" in local tests
  * 2023-08-20 - Update to YunoHost "Manifest v2"
  * 2023-02-19 - Replace devshell with a click CLI & replace pytest with normal unittests
* [v0.5.2](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.5.1...v0.5.2)
  * 2023-02-19 - Support Django 4.0: Add RedirectURLMixin from 4.1 as fallback
  * 2023-02-18 - Update via manageprojects
* [v0.5.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.5.0...v0.5.1)
  * 2022-12-21 - Disable assert_project_version in GitHub actions
* [v0.5.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.4.1...v0.5.0)
  * 2022-12-21 - include SSOwatLoginRedirectView
  * 2022-10-19 - Project upgrades
  * 2022-10-07 - "-pytest-darker" -> just call darker via test
  * 2022-10-05 - updates
* [v0.4.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.4.0...v0.4.1)
  * 2022-10-04 - v0.4.1 Add `assert_project_version` and `get_github_version_tag`
  * 2022-09-19 - Update requirements
  * 2022-09-19 - README
* [v0.4.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.3.0...v0.4.0)
  * 2022-09-15 - update django-tools to v0.54.0
  * 2022-09-15 - Run "saftey" check in CI
  * 2022-09-15 - update project setup tests
  * 2022-09-15 - Update requirements and release as v0.4.0rc6
  * 2022-09-15 - Silent "DEBUG=True" warning in tests
  * 2022-09-15 - Remove own assert_is_file() and assert_is_dir() implementation
  * 2022-09-15 - Update devshell.py via tests
  * 2022-08-25 - v0.4.0rc5 - better logging example settings
  * 2022-08-25 - v0.4.0rc4 - Add `SyslogHandler` to logging settings
  * 2022-08-25 - Lower systems checks "Error" to "Warning"
  * 2022-08-24 - remove unused "check_process"
  * 2022-08-24 - Update dev shell: Run a cmd2 App as CLI or shell
  * 2022-08-24 - Add system check to validate settings.LOG_LEVEL
  * 2022-08-24 - cleanup test settingsd
  * 2022-08-24 - Add systemcheck to validate all email addresses in settings
  * 2022-08-24 - __FINAL_HOME_PATH__ -> __FINALPATH__ and __FINAL_WWW_PATH__ -> __PUBLIC_PATH__
* [v0.3.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.5...v0.3.0)
  * 2022-08-14 - Update README
  * 2022-08-14 - update requirements
  * 2022-08-14 - code cleanup
  * 2022-08-14 - Add `extra_replacements:dict` to `create_local_test()`
  * 2022-08-14 - rename `setup_demo_user()` -> `setup_project_user()`
  * 2022-08-14 - Remove `pytest_helper.run_pytest()`
  * 2022-08-12 - Update README.md
* [v0.2.5](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.4...v0.2.5)
  * 2022-08-12 - bump version to v0.2.5
  * 2022-08-12 - Update README.md
  * 2022-08-12 - New variable names, for "ynh_add_config" usage
  * 2022-08-12 - update test setup
  * 2022-08-12 - fix line_length
  * 2022-08-12 - uses: codecov/codecov-action@v2
  * 2022-08-12 - fix editorconfig
  * 2022-07-11 - Expand local settings for local test.
* [v0.2.4](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.3...v0.2.4)
  * 2022-01-30 - Update README.md
  * 2022-01-30 - Use darker and pytest-darker as code formatter + update requirements
  * 2022-01-30 - Add/update some meta information
* [v0.2.3](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.2...v0.2.3)
  * 2022-01-07 - Bugfix tests
  * 2022-01-07 - update requirements
  * 2022-01-07 - Fix local test by set "SECURE_SSL_REDIRECT = False"
  * 2021-10-10 - Update README.md
* [v0.2.2](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.1...v0.2.2)
  * 2021-10-10 - Read YunoHost App name from project manifest.json file
* [v0.2.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.0...v0.2.1)
  * 2021-09-16 - Bugfix endless redirect loop, by adding `SECURE_PROXY_SSL_HEADER` to settings
  * 2021-09-15 - Update README.md
* [v0.2.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.5...v0.2.0)
  * 2021-09-15 - Update deps
  * 2021-08-17 - updtae README and add poetry.lock file
  * 2021-08-16 - Bugfix publish command
  * 2021-08-16 - fix "linting" and "fix_code_style" commands and remove obsolete Makefile
  * 2021-08-16 - fix flake8
  * 2021-08-16 - Set security settings
  * 2021-08-16 - Update githib actions
  * 2021-08-16 - Setup pytest against local test installation
  * 2021-02-28 - Rename/split from django_ynh
* [v0.1.5](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.4...v0.1.5)
  * 2021-01-19 - release v0.1.5
  * 2021-01-17 - Make some dependencies optional
* [v0.1.4](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.3...v0.1.4)
  * 2021-01-08 - prepare v0.1.4 release
  * 2021-01-08 - Bugfix #7 CSRF verification failed on POST requests
* [v0.1.3](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.2...v0.1.3)
  * 2021-01-08 - update README
  * 2021-01-08 - bump v0.1.3
  * 2021-01-08 - rename log file name in local test
  * 2021-01-08 - add homepage in pyproject.toml
  * 2020-12-29 - Update README.md
  * 2020-12-29 - update docs
  * 2020-12-29 - -volumes
  * 2020-12-29 - -pytest-randomly
  * 2020-12-29 - set "DEBUG = True" in local_test (so static files are served)
* [v0.1.2](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.1...v0.1.2)
  * 2020-12-29 - Bugfix nginx config
  * 2020-12-29 - copy conf/setup_user.py, too
  * 2020-12-29 - fix serve static files
  * 2020-12-29 - fix superuser setup
  * 2020-12-29 - Make "--email" optional in "create_superuser" manage command
* [v0.1.1](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.0...v0.1.1)
  * 2020-12-29 - pass existing pytest arguments
  * 2020-12-29 - fix code style
  * 2020-12-29 - update tests
  * 2020-12-29 - test version in scripts/_common.sh
  * 2020-12-29 - install the app via pip
  * 2020-12-29 - rename settings and urls
  * 2020-12-29 - Fix nginx.conf
  * 2020-12-29 - code cleanup
  * 2020-12-29 - Add more info about this project into README
  * 2020-12-29 - Generate "conf/requirements.txt" and use this file for install
  * 2020-12-29 - Add "django_ynh" to INSTALLED_APPS and migrate "create_superuser" to a manage command
* [v0.1.0](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/f578f14...v0.1.0)
  * 2020-12-28 - fix "make publish"
  * 2020-12-28 - fix linting
  * 2020-12-28 - fix version test
  * 2020-12-28 - bump version
  * 2020-12-28 - bugfix "make publish"
  * 2020-12-28 - remove test file
  * 2020-12-28 - +DocString
  * 2020-12-28 - code style
  * 2020-12-28 - call "make lint" as unittest
  * 2020-12-28 - +test_project_setup.py
  * 2020-12-28 - get pytest running with local test copy
  * 2020-12-28 - WIP: setup the project
  * 2020-12-23 - init

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)



## Links

* Report a bug about this package: https://github.com/YunoHost-Apps/django_yunohost_integration
* YunoHost website: https://yunohost.org/
* PyPi package: https://pypi.org/project/django_yunohost_integration/
