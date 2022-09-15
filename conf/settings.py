"""
    **************************************************************************
    Please do not modify this file, it will be reset at the next update.
    You can edit the file __FINALPATH__/local_settings.py and add/modify
    the settings you need.

    The parameters you add in local_settings.py will overwrite these,
    but you can use the options and documentation in this file to find out
    what can be done.
    **************************************************************************

    Django Settings here depends on YunoHost app settings.
"""
from pathlib import Path as __Path

from django_yunohost_integration.base_settings import *  # noqa:F401,F403
from django_yunohost_integration.secret_key import get_or_create_secret as __get_or_create_secret


FINALPATH = __Path('__FINALPATH__')  # /opt/yunohost/$app
assert FINALPATH.is_dir(), f'Directory not exists: {FINALPATH}'

PUBLIC_PATH = __Path('__PUBLIC_PATH__')  # /var/www/$app
assert PUBLIC_PATH.is_dir(), f'Directory not exists: {PUBLIC_PATH}'

LOG_FILE = __Path('__LOG_FILE__')  # /var/log/$app/$app.log
assert LOG_FILE.is_file(), f'File not exists: {LOG_FILE}'

PATH_URL = '__PATH_URL__'  # $YNH_APP_ARG_PATH
PATH_URL = PATH_URL.strip('/')

# -----------------------------------------------------------------------------
# config_panel.toml settings:

DEBUG_ENABLED = '__DEBUG_ENABLED__'
LOG_LEVEL = '__LOG_LEVEL__'
ADMIN_EMAIL = '__ADMIN_EMAIL__'

# Default email address to use for various automated correspondence from
# the site managers. Used for registration emails.
DEFAULT_FROM_EMAIL = '__DEFAULT_FROM_EMAIL__'

# -----------------------------------------------------------------------------

DEBUG = bool(int(DEBUG_ENABLED))

# -----------------------------------------------------------------------------

# Just for testing the "extra_replacements" argument of create_local_test():
EXTRA_REPLACEMENT = '__EXTRA_REPLACEMENT__'

# -----------------------------------------------------------------------------

# Function that will be called to finalize a user profile:
YNH_SETUP_USER = 'setup_user.setup_project_user'

SECRET_KEY = __get_or_create_secret(FINALPATH / 'secret.txt')  # /opt/yunohost/$app/secret.txt

ADMINS = (('__ADMIN__', '__ADMINMAIL__'),)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '__APP__',
        'USER': '__APP__',
        'PASSWORD': '__DB_PWD__',
        'HOST': '127.0.0.1',
        'PORT': '5432',  # Default Postgres Port
        'CONN_MAX_AGE': 600,
    }
}

# Title of site to use
SITE_TITLE = '__APP__'

# Site domain
SITE_DOMAIN = '__DOMAIN__'

# Subject of emails includes site title
EMAIL_SUBJECT_PREFIX = f'[{SITE_TITLE}] '


# E-mail address that error messages come from.
SERVER_EMAIL = ADMIN_EMAIL

# List of URLs your site is supposed to serve
ALLOWED_HOSTS = ['__DOMAIN__']


# _____________________________________________________________________________
# Configuration for caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/__REDIS_DB__',
        # If redis is running on same host as django_ynh, you might
        # want to use unix sockets instead:
        # 'LOCATION': 'unix:///var/run/redis/redis.sock?db=1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': '__APP__',
    },
}


# _____________________________________________________________________________
# Static files (CSS, JavaScript, Images)

if PATH_URL:
    STATIC_URL = f'/{PATH_URL}/static/'
    MEDIA_URL = f'/{PATH_URL}/media/'
else:
    # Installed to domain root, without a path prefix?
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

STATIC_ROOT = str(PUBLIC_PATH / 'static')
MEDIA_ROOT = str(PUBLIC_PATH / 'media')


# -----------------------------------------------------------------------------


# Set log file to e.g.: /var/log/$app/$app.log
LOGGING['handlers']['log_file']['filename'] = str(LOG_FILE)  # noqa:F405

# Example how to add logging to own app:
LOGGING['loggers']['django_yunohost_integration'] = {  # noqa:F405
    'handlers': ['syslog', 'log_file', 'mail_admins'],
    'level': 'INFO',
    'propagate': False,
}


# -----------------------------------------------------------------------------

try:
    from local_settings import *  # noqa:F401,F403
except ImportError:
    pass
