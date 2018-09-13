import functools
import io
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
def upload_file(zid, filepath, fp=None, stage='dev'):
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
def update_metadata(zid, metadata, stage='dev'):
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
def publish(zid, stage='dev'):
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "actions/publish?access_token={token}".format(zid=zid,
                                                      token=TOKENS[stage],
                                                      host=HOSTS[stage]))
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


@verify_token
def get(zid, stage='dev'):
    resp = requests.get(
        "{host}/api/deposit/depositions/{zid}"
        "?access_token={token}".format(zid=zid,
                                       token=TOKENS[stage],
                                       host=HOSTS[stage]))
    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


@verify_token
def list_items(stage='dev'):
    resp = requests.get(
        "{host}/api/deposit/depositions/?access_token={token}"
        .format(token=TOKENS[stage], host=HOSTS[stage]))

    if resp.status_code >= 300:
        raise ZenodoApiError(resp.json())
    return resp.json()


DROP_KEYS = ['ee', 'url', 'crossref', '@key', '@mdate']


def format_metadata(record, conferences):
    """Format a DBLP record for Zenodo, backfilling the right conference meta.

    Parameters
    ----------
    record : dict
        Paper record from DBLP.

    conferences : dict
        Metadata corresponding to each conference, keyed by year (str).

    Returns
    -------
    meta : dict
        Appropriately formated metadata for Zenodo.
    """

    new_rec = dict(communities=[dict(identifier='ismir')])
    new_rec.update(**{k: v for k, v in record.items() if k not in DROP_KEYS})
    new_rec.update(**conferences[new_rec['year']])
    authors = new_rec.pop('author')
    if authors and isinstance(authors, str):
        authors = [authors]

    new_rec['creators'] = [dict(name=_) for _ in authors]

    pages = new_rec.pop('pages', None)
    if pages:
        new_rec['partof_pages'] = pages

    return new_rec
