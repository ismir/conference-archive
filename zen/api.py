import functools
import io
import json
import logging
import requests
import os

logger = logging.getLogger("zen.api")

DEV = 'dev'
PROD = 'prod'
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
           'publish', 'list_items', 'ZenodoApiError']


class ZenodoApiError(BaseException):
    pass


def verify_token(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        stage = kwargs['stage']
        if TOKENS[stage] is None:
            raise ImportError("Access token for '{}' is unset.".format(stage))
        return func(*args, **kwargs)
    return wrapped


@verify_token
def create_id(stage=DEV):
    """Create a new Zenodo ID.

    Parameters
    ----------
    stage : str
        One of [dev, prod]; defines the deployment area to use.

    Returns
    -------
    zid : str or None
        Returns a string ID on success, or None.

    Raises
    ------
    ZenodoApiError on failure
    """
    resp = requests.post(
        "{host}/api/deposit/depositions?access_token={token}"
        .format(host=HOSTS[stage], token=TOKENS[stage]),
        data="{}", headers=HEADERS)

    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())

    return resp.json().get('id')


@verify_token
def upload_file(zid, filepath, fp=None, stage=DEV):
    '''Upload a filepath (local or URL) to zenodo, given an id.

    Parameters
    ----------
    zid : int
        Zenodo identifier

    filepath : str
        Path to a local file or a URL.

    fp : bytestring or file iterator, or None
        Optionally, the file pointer for uploading.
    '''
    basename = os.path.basename(filepath)
    fext = os.path.splitext(filepath)[-1].strip('.')
    if filepath.startswith('http') and fp is None:
        res = requests.get(filepath)
        fp = io.BytesIO(res.content)

    files = {'file': (basename, fp or open(filepath, 'rb'),
                      'application/{}'.format(fext))}
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "files?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                            host=HOSTS[stage]),
        files=files)
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())

    return resp.json()


@verify_token
def update_metadata(zid, metadata, stage=DEV):
    data = {"metadata": metadata}
    resp = requests.put(
        "{host}/api/deposit/depositions/{zid}"
        "?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                       host=HOSTS[stage]),
        data=json.dumps(data), headers=HEADERS)
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


@verify_token
def publish(zid, stage=DEV):
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "actions/publish?access_token={token}".format(zid=zid,
                                                      token=TOKENS[stage],
                                                      host=HOSTS[stage]))
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


@verify_token
def get(zid, stage=DEV):
    resp = requests.get(
        "{host}/api/deposit/depositions/{zid}"
        "?access_token={token}".format(zid=zid,
                                       token=TOKENS[stage],
                                       host=HOSTS[stage]))
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


@verify_token
def list_items(stage=DEV):
    resp = requests.get(
        "{host}/api/deposit/depositions/?access_token={token}"
        .format(token=TOKENS[stage], host=HOSTS[stage]))

    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()
