# This file will be copied to the "local test" files, to overwrite Django settings

import os


print('Load local settings file:', __file__)

ENV_TYPE = os.environ.get('ENV_TYPE', None)
print(f'ENV_TYPE: {ENV_TYPE!r}')

if ENV_TYPE == 'local':
    print(f'Activate settings overwrite by {__file__}')
    SECURE_SSL_REDIRECT = False  # Don't redirect http to https
    SERVE_FILES = True  # May used in urls.py
    AUTH_PASSWORD_VALIDATORS = []  # accept all passwords
    ALLOWED_HOSTS = ['*']  # For local dev. server
    CACHES = {  # Setup a working cache, without Redis ;)
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
    }
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'colorlog.StreamHandler',
                'formatter': 'standard',
            },
        },
        'loggers': {
            '': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
            'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
            'django_yunohost_integration': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
            'django_example': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        },
    }

elif ENV_TYPE == 'test':
    SILENCED_SYSTEM_CHECKS = ['security.W018']  # tests runs with DEBUG=True
    ALLOWED_HOSTS = []  # For unittests (Django's setup_test_environment() will add 'testserver')
