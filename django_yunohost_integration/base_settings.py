"""
    Base settings for a Django project installed in Yunohost.
    All values should not depent on YunoHost app settings.
"""
import logging as __logging


# -----------------------------------------------------------------------------
# settings that should be set in project settings:

SECRET_KEY = None

# -----------------------------------------------------------------------------

ROOT_URLCONF = 'urls'  # .../conf/urls.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',  # https://github.com/jazzband/django-axes
    'django_yunohost_integration.apps.YunohostIntegrationConfig',
]

# -----------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #
    # login a user via HTTP_REMOTE_USER header from SSOwat:
    'django_yunohost_integration.sso_auth.auth_middleware.SSOwatRemoteUserMiddleware',
    #
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #
    # AxesMiddleware should be the last middleware:
    'axes.middleware.AxesMiddleware',
]

# -----------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -----------------------------------------------------------------------------

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
LOGIN_URL = 'ssowat-login'
LOGOUT_REDIRECT_URL = '/yunohost/sso/'
# /yunohost/sso/?action=logout

# _____________________________________________________________________________

# Mark CSRF cookie as "secure" -> browsers sent cookie only with an HTTPS connection:
CSRF_COOKIE_SECURE = True

# Mark session cookie as "secure" -> browsers sent cookie only with an HTTPS connection:
SESSION_COOKIE_SECURE = True

# HTTP header/value combination that signifies a request is secure
# Your nginx.conf must set "X-Forwarded-Protocol" proxy header!
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# SecurityMiddleware should redirects all non-HTTPS requests to HTTPS:
SECURE_SSL_REDIRECT = True

# SecurityMiddleware should preload directive to the HTTP Strict Transport Security header:
SECURE_HSTS_PRELOAD = True

# Instruct modern browsers to refuse to connect to your domain name via an insecure connection:
SECURE_HSTS_SECONDS = 3600

# SecurityMiddleware should add the "includeSubDomains" directive to the Strict-Transport-Security
# header: All subdomains of your domain should be served exclusively via SSL!
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# _____________________________________________________________________________
# cut 'pathname' in log output

old_factory = __logging.getLogRecordFactory()


def cut_path(pathname, max_length):
    if len(pathname) <= max_length:
        return pathname
    return f'...{pathname[-(max_length - 3):]}'


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.cut_path = cut_path(record.pathname, 30)
    return record


__logging.setLogRecordFactory(record_factory)

# -----------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {module}.{funcName} {message}',
            'style': '{',
        },
        'colored': {  # https://github.com/borntyping/python-colorlog
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s %(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'colorlog.StreamHandler',
            'formatter': 'colored',
        },
        'mail_admins': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'log_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': '/tmp/django_yunohost_integration.log',  # <<< should be overwritten!
        },
        'syslog': {
            'level': 'INFO',
            'class': 'django_tools.log_utils.syslog_handler.SyslogHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['syslog', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['syslog', 'log_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['syslog', 'log_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
