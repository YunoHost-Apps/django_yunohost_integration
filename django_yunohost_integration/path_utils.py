from pathlib import Path


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
