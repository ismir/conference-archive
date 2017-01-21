import functools
import json
import logging
import requests
import os

logger = logging.getLogger("zen.api")

PREFIX = dict(
    dev="10.5072",
    prod="10.5281")
HOSTS = dict(
    dev='https://sandbox.zenodo.org',
    prod='https://zenodo.org')
TOKENS = dict(
    prod=os.environ.get("ZENODO_TOKEN_PROD"),
    dev=os.environ.get("ZENODO_TOKEN_DEV"))

HEADERS = {"Content-Type": "application/json"}
UPLOAD_TYPES = ['publication', 'poster', 'presentation', 'dataset',
                'image', 'video/audio', 'software', 'lesson']


__ALL__ = ['create_id', 'upload_file', 'update_metadata',
           'publish', 'get_items']


def verify_token(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        stage = kwargs['stage']
        if TOKENS[stage] is None:
            raise ImportError("Access token for '{}' is unset.".format(stage))
        return func(*args, **kwargs)
    return wrapped


@verify_token
def create_id(stage='dev'):
    """Create a new Zenodo ID.

    Parameters
    ----------
    stage : str
        One of [dev, prod]; defines the deployment area to use.

    Returns
    -------
    zid : str or None
        Returns a string ID on success, or None.
    """
    resp = requests.post(
        "{host}/api/deposit/depositions?access_token={token}"
        .format(host=HOSTS[stage], token=TOKENS[stage]),
        data="{}", headers=HEADERS)
    return resp.json().get('id', None)


@verify_token
def upload_file(zid, filename, stage='dev'):
    basename = os.path.basename(filename)
    data = {'filename': basename}
    files = {'file': open(filename, 'rb')}
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "files?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                            host=HOSTS[stage]),
        data=data, files=files)
    success = resp.status_code < 300
    logger.debug("Uploading file: success={}".format(success))
    return success


@verify_token
def update_metadata(zid, metadata, stage='dev'):
    data = {"metadata": metadata}
    resp = requests.put(
        "{host}/api/deposit/depositions/{zid}"
        "?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                       host=HOSTS[stage]),
        data=json.dumps(data), headers=HEADERS)
    success = resp.status_code < 300
    logger.debug("Updating metadata: success={}".format(success))
    return success


@verify_token
def publish(zid, stage='dev'):
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "actions/publish?access_token={token}".format(zid=zid,
                                                      token=TOKENS[stage],
                                                      host=HOSTS[stage]))
    success = resp.status_code < 300
    logger.debug("Publishing {}: success={}".format(zid, success))
    return success


@verify_token
def get_items(stage):
    pass
