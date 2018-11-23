import pytest

import os


@pytest.fixture()
def root_dir():
    return os.path.join(os.path.dirname(__file__), os.path.pardir)


@pytest.fixture()
def resources_dir():
    return os.path.join(os.path.dirname(__file__), 'resources')


@pytest.fixture()
def scripts_dir(root_dir):
    return os.path.join(root_dir, 'scripts')
