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
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']  # For local dev. server
    CACHES = {  # Setup a working cache, without Redis ;)
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
    }
elif ENV_TYPE == 'test':
    SILENCED_SYSTEM_CHECKS = ['security.W018']  # tests runs with DEBUG=True
    ALLOWED_HOSTS = []  # For unittests (Django's setup_test_environment() will add 'testserver')
