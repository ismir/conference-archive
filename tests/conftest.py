import pytest

import os


@pytest.fixture()
def resources_dir():
    return os.path.join(os.path.dirname(__file__), 'resources')
