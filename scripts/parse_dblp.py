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
import bs4
import logging
import json
import os
import requests
import sys
import time
import tqdm
import xmltodict

logger = logging.getLogger("mirror-dblp")

DBLP = "http://dblp.uni-trier.de/db/conf/ismir/ismir{year}.html"
XML = "https://dblp.uni-trier.de/rec/xml/{cite_key}.xml"


def get_cite_key(s):
    return s.split('/')[-1]


def collect_citekeys(year):
    """Recover paper metadata from DBLP given a conference year.

    Parameters
    ----------
    year : str or int
        Conference year (YYYY) to download.

    Returns
    -------
    cite_keys : list
        Collection of paper citation keys.
    """
    resp = requests.get(DBLP.format(year=str(year)))
    soup = bs4.BeautifulSoup(resp.text)
    records = soup.findAll(attrs={'class': 'entry inproceedings'})
    cite_keys = [rec.attrs.get('id') for rec in records]

    print("ISMIR{}: {} rows".format(year, len(cite_keys)))
    return cite_keys


def fetch_record(cite_key):
    resp = requests.get(XML.format(cite_key=cite_key))
    if resp.status_code >= 400:
        raise ValueError(XML.format(cite_key=cite_key))

    xml = resp.text.replace('\n', '')
    return dict(xmltodict.parse(xml)['dblp']['inproceedings'])


def main(output_file, num_cpus, verbose, resume=False, delay=0.5):
    cite_keys = []
    for year in range(2000, 2018):
        cite_keys += collect_citekeys(year)

    if resume and os.path.exists(output_file):
        with open(output_file, 'r') as fp:
            records = json.load(fp)
    else:
        records = dict()

    try:
        for ckey in tqdm.tqdm(cite_keys):
            now = time.time()
            if ckey not in records:
                records[ckey] = fetch_record(ckey)
                time.sleep(max([delay - (time.time() - now), 0]))

    except KeyboardInterrupt:
        print('Halting early')

    except ValueError as derp:
        print("Fetch failed: {}".format(derp))

    finally:
        print("Total {} rows".format(len(records)))
        with open(output_file, 'w') as fp:
            json.dump(records, fp, indent=2)

    return os.path.exists(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
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
