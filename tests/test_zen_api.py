import pytest

import os
import requests

import zen.api


OFFLINE = False
OFFLINE_REASON = 'Not online, skipping integration tests'
try:
    resp = requests.get('http://google.com')
except requests.ConnectionError as derp:
    OFFLINE |= True


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_api_create_id():
    assert zen.api.create_id(stage=zen.api.DEV) is not None


@pytest.fixture()
def pdf_file(resources_dir):
    return os.path.join(resources_dir, 'sample.pdf')


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_upload_file(pdf_file):
    zid = zen.api.create_id(stage=zen.api.DEV)
    result = zen.api.upload_file(zid, filepath=pdf_file, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert result is not None


@pytest.fixture()
def dummy_metadata():
    return dict(upload_type='blob')


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_api_update_metadata(dummy_metadata):
    zid = zen.api.create_id(stage=zen.api.DEV)
    resp = zen.api.update_metadata(zid, dummy_metadata, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert resp is not None


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_api_publish(dummy_metadata):
    zid = zen.api.create_id(stage=zen.api.DEV)
    zen.api.update_metadata(zid, dummy_metadata, stage=zen.api.DEV)
    resp = zen.api.publish(zid, stage=zen.api.DEV)

    # TODO: Verify something interesting here.
    assert resp is not None


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_api_get(dummy_metadata):
    zid = zen.api.create_id(stage=zen.api.DEV)
    zen.api.update_metadata(zid, dummy_metadata, stage=zen.api.DEV)
    resp1 = zen.api.publish(zid, stage=zen.api.DEV)
    resp2 = zen.api.get(zid, stage=zen.api.DEV)
    assert resp1 == resp2

    with pytest.raises(BaseException):
        zen.api.get(999999999999, stage=zen.api.DEV)


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_zen_api_list_items():
    results = zen.api.list_items(stage=zen.api.DEV)
    assert len(results) > 0
