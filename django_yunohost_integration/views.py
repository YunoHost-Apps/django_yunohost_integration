import logging
import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import redirect


logger = logging.getLogger(__name__)


def request_media_debug_view(request):
    """ debug request.META """

    assert settings.DEBUG is True, 'Only in DEBUG mode available!'

    if not request.user.is_authenticated:
        logger.info('Deny debug view: User not logged in!')
        UserModel = get_user_model()
        logger.info('Existing users are: %s', ', '.join(f'"{user}"' for user in UserModel.objects.all()))
        return redirect('admin:index')

    meta = pprint.pformat(request.META)
    html = f'<html><body>request.META: <pre>{meta}</pre></body></html>'

    return HttpResponse(html)
