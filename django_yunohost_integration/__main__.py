"""
    Allow django_yunohost_integration to be executable
    through `python -m django_yunohost_integration`.
"""

from django_yunohost_integration.cli_dev import main


if __name__ == '__main__':
    main()
