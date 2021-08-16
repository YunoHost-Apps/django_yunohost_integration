import sys
from pathlib import Path

import cmd2
from dev_shell.base_cmd2_app import DevShellBaseApp
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.config import DevShellConfig
from dev_shell.utils.subprocess_utils import verbose_check_call
from poetry_publish.publish import poetry_publish

import django_yunohost_integration
from django_yunohost_integration.local_test import create_local_test


PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent.parent
BASE_PATH = Path(django_yunohost_integration.__file__).parent.parent


def run_linters(cwd=None):
    """
    Run code formatters and linter
    """
    verbose_check_call(
        'flake8',
        cwd=cwd,
        exit_on_error=True
    )
    verbose_check_call(
        'isort', '--check-only', '.',
        cwd=cwd,
        exit_on_error=True
    )


class DevShellCommandSet(OriginDevShellCommandSet):

    # TODO:
    # pyupgrade --exit-zero-even-if-changed --py3-plus --py36-plus --py37-plus --py38-plus
    # `find . -name "*.py" -type f ! -path "./.tox/*" ! -path "./htmlcov/*" ! -path "*/volumes/*"

    def do_fix_code_style(self, statement: cmd2.Statement):
        """
        Fix code style by running: autopep8 and isort
        """
        verbose_check_call(
            'autopep8', '--aggressive', '--aggressive', '--in-place', '--recursive', '.',
            cwd=self.config.base_path
        )
        verbose_check_call(
            'isort', '.',
            cwd=self.config.base_path
        )

    def do_linting(self, statement: cmd2.Statement):
        """
        Linting: Check code style with flake8, isort and flynt
        """
        run_linters(cwd=self.config.base_path)

    def do_publish(self, statement: cmd2.Statement):
        """
        Publish "dev-shell" to PyPi
        """
        # don't publish if code style wrong:
        run_linters()

        # don't publish if test fails:
        verbose_check_call('pytest', '-x')

        poetry_publish(
            package_root=PACKAGE_ROOT,
            version=django_yunohost_integration.__version__,
        )


@cmd2.with_default_category('Django-YunoHost-Integration commands')
class DjangoYunoHostIntegrationCommandSet(DevShellBaseCommandSet):
    def do_local_test(self, statement: cmd2.Statement):
        """
        Build a "local_test" YunoHost installation and start the Django dev. server against it.
        See README for details ;)
        """
        create_local_test(
            django_settings_path=BASE_PATH / 'conf' / 'settings.py',
            destination=BASE_PATH / 'local_test',
            runserver=True,
        )


class DevShellApp(DevShellBaseApp):
    pass


def get_devshell_app_kwargs():
    """
    Generate the kwargs for the cmd2 App.
    (Separated because we needs the same kwargs in tests)
    """
    config = DevShellConfig(package_module=django_yunohost_integration)

    # initialize all CommandSet() with context:
    kwargs = dict(
        config=config
    )

    app_kwargs = dict(
        config=config,
        command_sets=[
            DjangoYunoHostIntegrationCommandSet(**kwargs),
            DevShellCommandSet(**kwargs),
        ]
    )
    return app_kwargs


def devshell_cmdloop():
    """
    Entry point to start the "dev-shell" cmd2 app.
    Used in: [tool.poetry.scripts]
    """
    c = DevShellApp(**get_devshell_app_kwargs())
    sys.exit(c.cmdloop())
