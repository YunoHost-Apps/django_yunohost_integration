import logging

from django.test import SimpleTestCase
from django_tools.utils.request import create_fake_request

from django_yunohost_integration.yunohost_utils import build_ssowat_uri, decode_ssowat_uri


class YunoHostUtilsTestCase(SimpleTestCase):
    def test_build_ssowat_uri(self):
        request = create_fake_request()
        self.assertEqual(request.get_host(), 'testserver')  # Default in Django tests ;)
        with self.assertLogs('django_yunohost_integration', level=logging.DEBUG) as logs:
            ssowat_uri = build_ssowat_uri(request=request, next_url='/foo/bar/')
        self.assertEqual(
            ssowat_uri,
            '/yunohost/sso/?r=aHR0cDovL3Rlc3RzZXJ2ZXIvZm9vL2Jhci8=',
        )
        self.assertEqual(
            logs.output,
            [
                "DEBUG:django_yunohost_integration.yunohost_utils:Built SSOWat next_uri='http://testserver/foo/bar/'",
            ],
        )
        self.assertEqual(  # check the encoded URL
            decode_ssowat_uri('aHR0cDovL3Rlc3RzZXJ2ZXIvZm9vL2Jhci8='),
            'http://testserver/foo/bar/',
        )
