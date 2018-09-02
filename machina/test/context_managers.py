import contextlib

import mock


# Originaly comes from mock-django (https://github.com/dcramer/mock-django)
@contextlib.contextmanager
def mock_signal_receiver(signal, wraps=None, **kwargs):
    """
    Temporarily attaches a receiver to the provided ``signal`` within the scope
    of the context manager.

    The mocked receiver is returned as the ``as`` target of the ``with``
    statement.

    To have the mocked receiver wrap a callable, pass the callable as the
    ``wraps`` keyword argument. All other keyword arguments provided are passed
    through to the signal's ``connect`` method.

    >>> with mock_signal_receiver(post_save, sender=Model) as receiver:
    >>>     Model.objects.create()
    >>>     assert receiver.call_count = 1
    """
    if wraps is None:
        wraps = lambda *args, **kwargs: None

    receiver = mock.Mock(wraps=wraps)
    signal.connect(receiver, **kwargs)
    yield receiver
    signal.disconnect(receiver)
