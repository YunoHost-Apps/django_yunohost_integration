from pathlib import Path

from poetry_publish.publish import poetry_publish
from poetry_publish.utils.subprocess_utils import verbose_check_call

import django_yunohost_integration
from django_yunohost_integration.path_utils import assert_is_file


PACKAGE_ROOT = Path(django_yunohost_integration.__file__).parent.parent


def publish():
    """
    Publish to PyPi
    Call this via:
        $ make publish
    """
    assert_is_file(PACKAGE_ROOT / 'README.md')

    verbose_check_call('make', 'pytest')  # don't publish if tests fail
    verbose_check_call('make', 'fix-code-style')  # don't publish if code style wrong

    poetry_publish(
        package_root=PACKAGE_ROOT,
        version=django_yunohost_integration.__version__,
    )


if __name__ == '__main__':
    publish()
