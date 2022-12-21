from importlib.metadata import version


__version__ = version('django_yunohost_integration')


# The currently supported major YunoHost version (Used in system checks)
SUPPORTED_YUNOHOST_MAJOR_VER = 11
