import pytest

import os

import zen.api


def test_zen_api_create_id():
    assert zen.api.create_id(stage=zen.api.DEV) is not None


@pytest.fixture()
def pdf_file(resources_dir):
    return os.path.join(resources_dir, 'sample.pdf')


def test_zen_upload_file(pdf_file):
    zid = zen.api.create_id(stage=zen.api.DEV)
    result = zen.api.upload_file(zid, filepath=pdf_file, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert result is not None


@pytest.fixture()
def dummy_metadata():
    return dict(upload_type='blob')


def test_zen_api_update_metadata(dummy_metadata):
    zid = zen.api.create_id(stage=zen.api.DEV)
    resp = zen.api.update_metadata(zid, dummy_metadata, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert resp is not None


def test_zen_api_publish(dummy_metadata):
    zid = zen.api.create_id(stage=zen.api.DEV)
    zen.api.update_metadata(zid, dummy_metadata, stage=zen.api.DEV)
    resp = zen.api.publish(zid, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert resp is not None


def test_zen_api_get():
    pass


def test_zen_api_list_items():
    pass
