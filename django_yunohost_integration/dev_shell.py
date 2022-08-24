from pathlib import Path

import cmd2
from dev_shell.base_cmd2_app import DevShellBaseApp, run_cmd2_app
from dev_shell.command_sets import DevShellBaseCommandSet
from dev_shell.command_sets.dev_shell_commands import DevShellCommandSet as OriginDevShellCommandSet
from dev_shell.config import DevShellConfig
from dev_shell.utils.subprocess_utils import verbose_check_call
from poetry_publish.publish import poetry_publish

import django_yunohost_integration
from django_yunohost_integration.local_test import create_local_test


PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent


class DevShellCommandSet(OriginDevShellCommandSet):
    def do_publish(self, statement: cmd2.Statement):
        """
        Publish "dev-shell" to PyPi
        """
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
            django_settings_path=PACKAGE_ROOT / 'conf' / 'settings.py',
            destination=PACKAGE_ROOT / 'local_test',
            runserver=True,
            extra_replacements={'__DEBUG_ENABLED__': '1'},
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
    kwargs = dict(config=config)

    app_kwargs = dict(
        config=config,
        command_sets=[
            DjangoYunoHostIntegrationCommandSet(**kwargs),
            DevShellCommandSet(**kwargs),
        ],
    )
    return app_kwargs


def devshell_cmdloop():
    """
    Entry point to start the "dev-shell" cmd2 app.
    Used in: [tool.poetry.scripts]
    """
    app = DevShellApp(**get_devshell_app_kwargs())
    run_cmd2_app(app)  # Run a cmd2 App as CLI or shell
