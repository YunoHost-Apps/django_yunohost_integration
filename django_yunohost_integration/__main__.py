"""
    Allow django_yunohost_integration to be executable
    through `python -m django_yunohost_integration`.
"""

from django_yunohost_integration.cli.dev import cli


def main():
    cli()


if __name__ == '__main__':
    main()
