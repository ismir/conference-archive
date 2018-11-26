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


@pytest.fixture()
def pdf_file(resources_dir):
    return os.path.join(resources_dir, 'sample.pdf')
