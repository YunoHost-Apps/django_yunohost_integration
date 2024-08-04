import subprocess
from unittest import TestCase

from bx_py_utils.path import assert_is_file

from django_yunohost_integration.path_utils import get_project_root


class ProjectSetupTestCase(TestCase):
    def test_manage_local_test_check(self):
        manage_local_test_bin = get_project_root() / 'manage_local_test.py'
        assert_is_file(manage_local_test_bin)

        output = subprocess.check_output([manage_local_test_bin, 'check'], text=True)
        self.assertIn('Setup local YunoHost package', output)
        self.assertIn('django_yunohost_integration/local_test/', output)
