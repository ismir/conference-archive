import pytest

import json
import os

import upload_to_zenodo
import zen


OFFLINE = not zen.api._is_online()
OFFLINE_REASON = 'not connected to the internet'


@pytest.fixture()
def proceedings_file(resources_dir):
    return os.path.join(resources_dir, 'sample-papers.json')


@pytest.fixture()
def conferences_file(resources_dir):
    return os.path.join(resources_dir, 'sample-confs.json')


@pytest.fixture()
def proceedings(proceedings_file):
    return json.load(open(proceedings_file, 'r'))


@pytest.fixture()
def conferences(proceedings_file):
    return json.load(open(proceedings_file, 'r'))


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_upload_to_zenodo_upload(proceedings, conferences, tmpdir):
    result = upload_to_zenodo.upload(proceedings[0], conferences, stage=zen.DEV)
    assert result['zenodo_id'] is not None
    assert result['ee'].startswith('http')
    assert result['url'].startswith('http')

    with open(os.path.join(str(tmpdir), 'output.json'), 'w') as fp:
        json.dump(result, fp, indent=2)


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_upload_to_zenodo_archive(proceedings, conferences, tmpdir):
    results = upload_to_zenodo.upload(proceedings, conferences, stage=zen.DEV)
    assert len(results) == len(proceedings)

    with open(os.path.join(str(tmpdir), 'outputs.json'), 'w') as fp:
        json.dump(results, fp, indent=2)


@pytest.mark.skipif(OFFLINE, reason=OFFLINE_REASON)
def test_upload_to_zenodo_main(proceedings_file, conferences_file, scripts_dir, tmpdir):
    script = os.path.join(scripts_dir, 'upload_to_zenodo.py')
    output_file = os.path.join(str(tmpdir), 'test_output.json')

    os.system('{} {} {} --stage dev'.format(script, proceedings_file, conferences_file, output_file))
