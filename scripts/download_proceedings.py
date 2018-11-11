#!/usr/bin/env python
# coding: utf8
"""Download PDF proceedings given a metadata dump.

Usage
-----

$ python ./scripts/download_proceedigns.py \
    proceedings.json \
    ./path/to/pdfs

"""

import argparse
from joblib import Parallel, delayed
import json
import os
import random
import requests
import sys
import tqdm


def download_pdf(fid, url, year, dst):

    # create output dir
    os.makedirs(os.path.join(dst, year), exist_ok=True)

    fout = os.path.join(dst, year, '{}.pdf'.format(fid))

    if isinstance(url, list):
        for _ in url:
            if _.endswith('pdf'):
                url = _
                break

    if url is None:
        print('missing url for {}'.format(fid))

    elif not os.path.exists(fout):
        res = requests.get(url)
        with open(fout, 'wb') as fp:
            fp.write(res.content)

    return os.path.exists(fout)


def main(records, output_dir, num_cpus, verbose):

    pdfs = []

    for cur_key in records.keys():
        cur_fn = cur_key.split('/')[-1]

        cur_year = str(records[cur_key]['year'])

        try:
            cur_url = records[cur_key]['ee']
            pdfs.append((cur_fn, cur_url, cur_year))
        except KeyError:
            print('{}: No URL available.'.format(cur_fn))
            cur_url = ''

    items = pdfs
    random.shuffle(items)

    dfx = delayed(download_pdf)
    pool = Parallel(n_jobs=num_cpus, verbose=verbose)

    return all(pool(dfx(*kv, dst=output_dir) for kv in tqdm.tqdm(items)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("metadata_file",
                        metavar="metadata_file", type=str,
                        help="JSON dump of metadata records.")
    parser.add_argument("output_dir",
                        metavar="output_dir", type=str,
                        help="Path to write the downloaded PDFs.")
    parser.add_argument("--num_cpus",
                        metavar="num_cpus", type=int, default=-2,
                        help="Number of CPUs to use in parallel.")
    parser.add_argument("--verbose",
                        metavar="verbose", type=int, default=0,
                        help="Verbosity level for joblib.")
    args = parser.parse_args()

    with open(args.metadata_file, 'r') as fp:
        records = json.load(fp)

    success = main(records, args.output_dir, args.num_cpus, args.verbose)
    sys.exit(0 if success else 1)
