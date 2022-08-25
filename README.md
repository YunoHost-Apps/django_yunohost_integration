# django_yunohost_integration

[![pytest](https://github.com/YunoHost-Apps/django_yunohost_integration/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/YunoHost-Apps/django_yunohost_integration/actions/workflows/pytest.yml) [![Coverage Status on codecov.io](https://codecov.io/gh/YunoHost-Apps/django_yunohost_integration/branch/main/graph/badge.svg)](https://codecov.io/gh/YunoHost-Apps/django_yunohost_integration)

[![django_yunohost_integration @ PyPi](https://img.shields.io/pypi/v/django_yunohost_integration?label=django_yunohost_integration%20%40%20PyPi)](https://pypi.org/project/django_yunohost_integration/)
[![Python Versions](https://img.shields.io/pypi/pyversions/django_yunohost_integration)](https://gitlab.com/YunoHost-Apps/django_yunohost_integration/-/blob/main/pyproject.toml)
[![License GPL](https://img.shields.io/pypi/l/django_yunohost_integration)](https://gitlab.com/YunoHost-Apps/django_yunohost_integration/-/blob/main/LICENSE)


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
* Helper to run `pytest` against `local_test` "installation"


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

FINALPATH = __Path('__FINALPATH__')  # /opt/yunohost/$app
assert FINALPATH.is_dir(), f'Directory not exists: {FINALPATH}'

PUBLIC_PATH = __Path('__PUBLIC_PATH__')  # /var/www/$app
assert PUBLIC_PATH.is_dir(), f'Directory not exists: {PUBLIC_PATH}'

LOG_FILE = __Path('__LOG_FILE__')  # /var/log/$app/$app.log
assert LOG_FILE.is_file(), f'File not exists: {LOG_FILE}'

PATH_URL = '__PATH_URL__'  # $YNH_APP_ARG_PATH
PATH_URL = PATH_URL.strip('/')

# -----------------------------------------------------------------------------

# Function that will be called to finalize a user profile:
YNH_SETUP_USER = 'setup_user.setup_project_user'

SECRET_KEY = __get_or_create_secret(FINALPATH / 'secret.txt')  # /opt/yunohost/$app/secret.txt

# INSTALLED_APPS.append('<insert-your-app-here>')

# -----------------------------------------------------------------------------
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
~/django_yunohost_integration$ ./devshell.py

+ .venv/bin/python .venv/bin/devshell



Developer shell - django_yunohost_integration - v0.2.0


Documented commands (use 'help -v' for verbose/'help <topic>' for details):

dev-shell commands
==================
fix_code_style  linting  list_venv_packages  publish  pytest  update


Django-YunoHost-Integration commands
====================================
local_test

Uncategorized
=============
alias  help     macro  run_pyscript  set    shortcuts
edit   history  quit   run_script    shell


(django_yunohost_integration)
```

For quicker developing of django_yunohost_integration in the context of YunoHost app,
it's possible to run the Django developer server with the settings
and urls made for YunoHost installation.

e.g.:
```bash
~/django_yunohost_integration$ ./devshell.py
(django_yunohost_integration) local_test
```

* SQlite database will be used
* A super user with username `test` and password `test` is created
* The page is available under `http://127.0.0.1:8000/app_path/`


## history

* [**dev**](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.4.0rc4...main)
  * tbc
* [v0.4.0rc4 - 25.08.2022](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.3.0...v0.4.0rc4)
  * Add `SyslogHandler` to logging settings
  * rename replacements (but still support the old ones):
    * `__FINAL_HOME_PATH__` -> `__FINALPATH__`
    * `__FINAL_WWW_PATH__` -> `__PUBLIC_PATH__`
  * Add system checks to verify all "EMAIL" in `settings` and `settings.LOG_LEVEL`
  * Bugfix dev shell and exit if it's called as CLI
* [v0.3.0 - 14.08.2022](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.5...v0.3.0)
  * Add `extra_replacements:dict` argument to `create_local_test()` to pass own `__YNH_VARIABLE__` replacements
  * Remove `pytest_helper.run_pytest()` because every project should used a own [conftest.py](https://github.com/YunoHost-Apps/django_yunohost_integration/blob/main/tests/conftest.py) with `create_local_test()` usage.
* [v0.2.5 - 12.08.2022](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.4...v0.2.5)
  * Support new variable names, for `ynh_add_config` usage in local test helper.
  * Run tests with Python v3.10, too.
  * Update project setup.
* [v0.2.4 - 30.01.2022](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.3...v0.2.4)
  * Rename git "master" branch to "main"
  * Use darker and pytest-darker as code formatter + update requirements
* [v0.2.3 - 07.01.2022](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.2...v0.2.3)
  * Bugfix Fix local test by set `"SECURE_SSL_REDIRECT = False"`
* [v0.2.2 - 10.10.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.1...v0.2.2)
  * Read YunoHost App Id from "manifest.json" and check root directory name
* [v0.2.1 - 16.09.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.2.0...v0.2.1)
  * Bugfix endless redirect loop, by adding `SECURE_PROXY_SSL_HEADER` to settings
* [v0.2.0 - 15.09.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.5...v0.2.0)
  * rename/split `django_ynh` into:
    * [django_yunohost_integration](https://github.com/YunoHost-Apps/django_yunohost_integration) - Python package with the glue code to integrate a Django project with YunoHost
    * [django_example_ynh](https://github.com/YunoHost-Apps/django_example_ynh) - Demo YunoHost App to demonstrate the integration of a Django project under YunoHost
  * Replace `psycopg2-binary` with `psycopg2` (needs some prerequisites packages, see above)
* [v0.1.5 - 19.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.4...v0.1.5)
  * Make some deps `gunicorn`, `psycopg2-binary`, `django-redis`, `django-axes` optional
* [v0.1.4 - 08.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.3...v0.1.4)
  * Bugfix: CSRF verification failed on POST requests
* [v0.1.3 - 08.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.2...v0.1.3)
  * set "DEBUG = True" in local_test (so static files are served and auth works)
  * Bugfixes and cleanups
* [v0.1.2 - 29.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.1...v0.1.2)
  * Bugfixes
* [v0.1.1 - 29.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.0...v0.1.1)
  * Refactor "create_superuser" to a manage command, useable via "django_yunohost_integration" in `INSTALLED_APPS`
  * Generate "conf/requirements.txt" and use this file for install
  * rename own settings and urls (in `/conf/`)
* [v0.1.0 - 28.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/f578f14...v0.1.0)
  * first working state
* [23.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/commit/f578f144a3a6d11d7044597c37d550d29c247773)
  * init the project


## Links

* Report a bug about this package: https://github.com/YunoHost-Apps/django_yunohost_integration
* YunoHost website: https://yunohost.org/
* PyPi package: https://pypi.org/project/django_yunohost_integration/
