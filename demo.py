"""Uploader demo for Zenodo.

To Use
------
You must set / export two environment variables for access to Zenodo;

```
export ZENODO_TOKEN_PROD=<PRIMARY_TOKEN>
export ZENODO_TOKEN_DEV=<SANDBOX_TOKEN>
```

Note: This script will yell loudly if the requested token is unset.

Now, you can then upload the sample data to the development site:
```
$ python demo.py data/sample_paper.pdf data/sample_metadata.json dev
```
"""
import argparse
import logging
import os
import json
import requests
import sys

logger = logging.getLogger("demo_upload")

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


def upload(filename, metadata, stage, zid=None):
    """Upload a file / metadata pair to a Zenodo stage.

    Parameters
    ----------
    filename : str
        Path to a local file on disk.
        TODO: Could be a generic URI, to allow webscraping at the same time.

    metadata : dict
        Metadata associated with the resource.

    stage : str
        One of [dev, prod]; defines the deployment area to use.

    zid : str, default=None
        If provided, attempts to update the resource for the given Zenodo ID.

    Returns
    -------
    success : bool
        True on successful upload, otherwise False.
    """
    success = True
    if zid is None:
        resp = requests.post(
            "{host}/api/deposit/depositions?access_token={token}"
            .format(host=HOSTS[stage], token=TOKENS[stage]),
            data="{}", headers=HEADERS)
        zid = resp.json().get('id')
        success &= (resp.status_code < 300)
        logger.debug("Creating Zenodo ID: success={}".format(success))

    basename = os.path.basename(filename)
    data = {'filename': basename}
    files = {'file': open(filename, 'rb')}
    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "files?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                            host=HOSTS[stage]),
        data=data, files=files)
    success &= (resp.status_code < 300)
    logger.debug("Uploading file: success={}".format(success))

    data = {"metadata": metadata}
    resp = requests.put(
        "{host}/api/deposit/depositions/{zid}"
        "?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                       host=HOSTS[stage]),
        data=json.dumps(data), headers=HEADERS)
    success &= (resp.status_code < 300)
    logger.debug("Updating metadata: success={}".format(success))

    resp = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "actions/publish?access_token={token}".format(zid=zid,
                                                      token=TOKENS[stage],
                                                      host=HOSTS[stage]))
    success &= (resp.status_code < 300)
    logger.debug("Publishing: success={}".format(success))
    return success


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("filename",
                        metavar="filename", type=str,
                        help="Path to a PDF file to upload.")
    parser.add_argument("metadata",
                        metavar="metadata", type=str,
                        help="Path to a JSON file of metadata to upload")
    parser.add_argument("stage",
                        metavar="stage", type=str,
                        help="Stage to execute.")
    args = parser.parse_args()

    if TOKENS[args.stage] is None:
        raise ValueError("Access token for '{}' is unset.".format(args.stage))

    metadata = json.load(open(args.metadata))
    success = upload(args.filename, metadata, args.stage)
    logging.info("Complete upload: success={}".format(success))
    sys.exit(0 if success else 1)
