from cli_base.cli_tools.test_utils.cli_readme import assert_cli_help_in_readme
from cli_base.cli_tools.test_utils.rich_test_utils import NoColorEnvRichClick, invoke
from manageprojects.tests.base import BaseTestCase

from django_yunohost_integration import constants
from django_yunohost_integration.cli_dev import PACKAGE_ROOT


README_PATH = PACKAGE_ROOT / 'README.md'


class ReadmeTestCase(BaseTestCase):

    def test_dev_help(self):
        with NoColorEnvRichClick(width=120):
            stdout = invoke(cli_bin=PACKAGE_ROOT / 'dev-cli.py', args=['--help'], strip_line_prefix='usage: ')
        self.assert_in_content(
            got=stdout,
            parts=(
                'usage: ./dev-cli.py [-h]',
                ' check-code-style ',
                ' coverage ',
                constants.CLI_EPILOG,
            ),
        )
        assert_cli_help_in_readme(
            readme_path=README_PATH, text_block=stdout, marker='dev help', cli_epilog=constants.CLI_EPILOG
        )
