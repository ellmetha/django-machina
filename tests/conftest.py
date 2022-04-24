import os
import shutil

import pytest

from . import settings


@pytest.fixture(scope='session', autouse=True)
def empty_media():
    """ Removes the directories inside the MEDIA_ROOT that could have been filled during tests. """
    yield
    for candidate in os.listdir(settings.MEDIA_ROOT):
        path = os.path.join(settings.MEDIA_ROOT, candidate)
        try:
            shutil.rmtree(path)
        except OSError:
            pass
