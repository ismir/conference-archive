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
$ python scripts/archive_collection.py \
    data/proceedings-updated.json \
    data/conferences.json \
    dev \
    --verbose 50 \
    --num_cpus -2 \
    --max_items 10
```
"""
import argparse
import io
from joblib import Parallel, delayed
import json
import logging
import os
import random
import requests
import sys

import zen

logger = logging.getLogger("fetch")

META = {
    "license": "CC-BY-4.0",
    "access_right": "open",
    "description": "<p></p>",
    "communities": [{"identifier": "ismir"}],
    "imprint_publisher": "ISMIR",
    "upload_type": "publication",
    "publication_type": "conferencepaper"
}


def build_record(record, conferences):
    record = dict(**record)
    key = record['conference_acronym']
    meta = META.copy()
    meta.update(**conferences[key])
    meta["partof_title"] = meta.pop('conference_title')
    meta['conference_title'] = meta["partof_title"].split("the ")[-1]
    meta["imprint_place"] = meta["conference_place"]
    res = requests.get(record.pop('pdf_url'))
    fp = io.BytesIO(res.content)
    meta.update(**record)
    return os.path.basename(res.url), fp, meta


def upload(record, conferences, stage):
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
    """
    if not record['pdf_url'].lower().endswith('.pdf'):
        return

    fname, fp, meta = build_record(record, conferences)
    zid = zen.create_id(stage=stage)
    zen.upload_file(zid, fname, fp=fp, stage=stage)
    zen.update_metadata(zid, meta, stage=stage)
    return zen.publish(zid, stage=stage).get('submitted', False)


def archive(proceedings, conferences, stage, num_cpus=-2, verbose=0):
    pool = Parallel(n_jobs=num_cpus, verbose=verbose)
    fx = delayed(upload)
    return all(pool(fx(rec, conferences, stage) for rec in proceedings))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("proceedings",
                        metavar="proceedings", type=str,
                        help="Path to proceedings records.")
    parser.add_argument("conferences",
                        metavar="conferences", type=str,
                        help="Path to a JSON file of conference metadata.")
    parser.add_argument("stage",
                        metavar="stage", type=str,
                        help="Stage to execute.")
    parser.add_argument("--num_cpus",
                        metavar="num_cpus", type=int, default=-2,
                        help="Number of CPUs to use in parallel.")
    parser.add_argument("--verbose",
                        metavar="verbose", type=int, default=0,
                        help="Verbosity level for joblib.")
    parser.add_argument("--max_items",
                        metavar="max_items", type=int, default=None,
                        help="Maximum number of items to upload.")
    args = parser.parse_args()
    proceedings = [rec for year in json.load(open(args.proceedings))
                   for rec in year]
    conferences = json.load(open(args.conferences))

    if args.max_items is not None:
        random.shuffle(proceedings)
        proceedings = proceedings[:args.max_items]

    success = archive(proceedings, conferences, args.stage,
                      args.num_cpus, args.verbose)
    sys.exit(0 if success else 1)
