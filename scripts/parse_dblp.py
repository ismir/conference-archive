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
from joblib import Parallel, delayed
import json
import os
import requests
import sys

logger = logging.getLogger("demo_upload")

DBLP = "http://dblp.uni-trier.de/db/conf/ismir/ismir{year}.html"


def extract_proceedings(year):
    """Recover paper metadata from DBLP given a conference year.

    Parameters
    ----------
    year : str or int
        Conference year (YYYY) to download.

    Returns
    -------
    records : list
        Collection of dictionaries containing paper details.
    """
    resp = requests.get(DBLP.format(year=str(year)))
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    records = soup.findAll(attrs={'class': 'entry inproceedings'})
    data = []
    for rec in records:
        creators = [auth.text for auth in rec(itemprop='author')]
        title = rec(**{'class': 'title'})[0].text
        pdf_url = rec(**{'class': 'head'})[0].find_next("a")['href']
        data += [dict(creators=creators, title=title, pdf_url=pdf_url,
                      conference_acronym="ISMIR{}".format(year))]
    return data


def main(output_file, num_cpus, verbose):
    pool = Parallel(n_jobs=num_cpus, verbose=verbose)
    fx = delayed(extract_proceedings)
    results = pool(fx(year) for year in range(2000, 2017))
    with open(output_file, 'w') as fp:
        json.dump(results, fp)
    return os.path.exists(output_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
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
    args = parser.parse_args()
    success = main(args.output_file, args.num_cpus, args.verbose)
    logging.info("Complete scrape: success={}".format(success))
    sys.exit(0 if success else 1)
