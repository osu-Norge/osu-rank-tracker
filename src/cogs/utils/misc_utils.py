

from contextlib import contextmanager


@contextmanager
def ignore_exception(*exceptions: Exception):
    """
    Ignores the given exceptions
    Parameters
    ----------
    *exceptions tuple[Exception]: The exceptions you want to ignore
    """

    try:
        yield
    except exceptions:
        pass
