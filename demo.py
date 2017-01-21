"""
"""

import argparse
import logging
import os
import json
import requests


logger = logging.getLogger("demo_upload")
logging.basicConfig(level=logging.DEBUG)

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
    if zid is None:
        r = requests.post(
            "{host}/api/deposit/depositions?access_token={token}"
            .format(host=HOSTS[stage], token=TOKENS[stage]),
            data="{}", headers=HEADERS)
        zid = r.json().get('id')

    basename = os.path.basename(filename)
    data = {'filename': basename}
    files = {'file': open(filename, 'rb')}
    r = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "files?access_token={token}".format(zid=zid, token=TOKENS[stage],
                                            host=HOSTS[stage]),
        data=data, files=files)

    print(r.status_code, r.json())

    data = {"metadata": metadata}

    r = requests.put("{host}/api/deposit/depositions/{zid}"
                     "?access_token={token}".format(zid=zid,
                                                    token=TOKENS[stage],
                                                    host=HOSTS[stage]),
                     data=json.dumps(data), headers=HEADERS)
    print(r.status_code)
    r = requests.post(
        "{host}/api/deposit/depositions/{zid}/"
        "actions/publish?access_token={token}".format(zid=zid,
                                                      token=TOKENS[stage],
                                                      host=HOSTS[stage]))
    print(r.status_code, r.json())


if __name__ == '__main__':
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
    metadata = json.load(open(args.metadata))
    upload(args.filename, metadata, args.stage)
