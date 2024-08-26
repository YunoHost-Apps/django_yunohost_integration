from unittest import TestCase

from django_yunohost_integration.install_python.install_python import extract_versions, get_latest_versions


PYTHON_ORG_FTP_HTML = """
<a href="3.11.7/">3.11.7/</a>                                            04-Dec-2023 21:53                   -
<a href="3.11.8/">3.11.8/</a>                                            06-Feb-2024 23:40                   -
<a href="3.11.9/">3.11.9/</a>                                            02-Apr-2024 13:39                   -
<a href="3.12.0/">3.12.0/</a>                                            02-Oct-2023 14:50                   -
<a href="3.12.1/">3.12.1/</a>                                            08-Dec-2023 00:41                   -
<a href="3.12.2/">3.12.2/</a>                                            06-Feb-2024 23:57                   -
<a href="3.12.3/">3.12.3/</a>                                            09-Apr-2024 15:28                   -
<a href="3.12.4/">3.12.4/</a>                                            06-Jun-2024 22:25                   -
<a href="3.12.5/">3.12.5/</a>                                            07-Aug-2024 11:36                   -
<a href="3.13.0/">3.13.0/</a>                                            05-Aug-2024 13:18                   -
<a href="3.14.0/">3.14.0/</a>                                            27-Jul-2024 13:19                   -
"""


class TestGetLatestPythonVersion(TestCase):
    def test_extract_versions(self):
        self.assertEqual(
            extract_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.11'),
            ['3.11.9', '3.11.8', '3.11.7'],
        )
        self.assertEqual(
            extract_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.12'),
            ['3.12.5', '3.12.4', '3.12.3', '3.12.2', '3.12.1', '3.12.0'],
        )
        self.assertEqual(
            extract_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.13'),
            ['3.13.0'],
        )

    def test_get_latest_versions(self):
        self.assertEqual(get_latest_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.11'), '3.11.9')
        self.assertEqual(get_latest_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.12'), '3.12.5')
        self.assertEqual(get_latest_versions(html=PYTHON_ORG_FTP_HTML, major_version='3.13'), '3.13.0')
