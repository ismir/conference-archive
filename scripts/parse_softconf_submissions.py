#!/usr/bin/env python
# coding: utf8
"""Download metadata from the DBLP archive.

Usage
-----
```
$ python scripts/parse_dblp.py proceedings.json
```
"""
import argparse
import logging
import json
import os
import pandas as pd
import sys
import time
import tqdm

import zen.models


def parse_one(rec):
    pass


def parse_csv(fname, encoding='utf-16'):
    df = pd.read_csv(fname, encoding=encoding, index_col=0)
    return df.apply(parse_one, axis=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("csv_file",
                        metavar="csv_file", type=str,
                        help="Path to a CSV file of submissions.")
    parser.add_argument("output_file",
                        metavar="output_file", type=str,
                        help="Path to write the output metadata as JSON.")
    parser.add_argument("--num_cpus",
                        metavar="num_cpus", type=int, default=-2,
                        help="Number of CPUs to use in parallel.")
    parser.add_argument("--verbose",
                        metavar="verbose", type=int, default=0,
                        help="Verbosity level for joblib.")
    parser.add_argument("--resume",
                        action='store_true',
                        help="If given, will resume")
    parser.add_argument("--delay",
                        type=float, default=0.5,
                        help="Delay time in seconds between XML requests.")
    args = parser.parse_args()
    success = main(args.output_file, args.num_cpus, args.verbose,
                   args.resume, args.delay)
    logging.info("Complete scrape: success={}".format(success))
    sys.exit(0 if success else 1)
