"""
    Helper to create a random string for settings.SECRET_KEY

    SECURITY WARNING: keep the secret key used in production secret!
"""
import logging
from pathlib import Path
from secrets import token_urlsafe


logger = logging.getLogger(__name__)


def get_or_create_secret(secret_file):
    assert isinstance(secret_file, Path)
    assert secret_file.parent.is_dir, f'Directory does not exists: {secret_file.parent}'

    if not secret_file.is_file():
        logger.info('Generate %s', secret_file)
        secret_file.open('w').write(token_urlsafe(128))

    with secret_file.open('r') as f:
        return f.read()
