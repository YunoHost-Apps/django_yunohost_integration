from functools import cache
from pathlib import Path

from bx_py_utils.path import assert_is_file


def is_relative_to(p, other):
    """
    Path.is_relative_to() is new in Python 3.9
    """
    p = Path(p)
    other = Path(other)
    try:
        p.relative_to(other)
    except ValueError:
        return False
    else:
        return True


@cache
def get_project_root() -> Path:
    cwd = Path.cwd()
    pyproject_toml_path = cwd / 'pyproject.toml'
    try:
        assert_is_file(pyproject_toml_path)
    except AssertionError as err:
        raise AssertionError(f'Please start script from git root directory: {err}')
    return cwd
