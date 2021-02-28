from pathlib import Path


def assert_is_dir(dir_path):
    assert isinstance(dir_path, Path)
    assert dir_path.is_dir(), f'Directory does not exists: {dir_path}'


def assert_is_file(file_path):
    assert isinstance(file_path, Path)
    file_path.resolve()
    assert file_path.is_file(), f'File not found: {file_path}'


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
