"""
    Base settings for a Django project installed in Yunohost.
    All values should not depent on YunoHost app settings.
"""


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
    'django_yunohost_integration',
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
LOGIN_URL = '/yunohost/sso/'
LOGOUT_REDIRECT_URL = '/yunohost/sso/'
# /yunohost/sso/?action=logout

# _____________________________________________________________________________
# Setting below, should be overwritten!

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {module}.{funcName} {message}',
            'style': '{',
        },
    },
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'}},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.auth': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django.security': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'django_yunohost_integration': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
