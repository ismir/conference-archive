#!/usr/bin/env python
"""Render conference metadata to markdown

Functionality to export proceedings records to markdown.

Example usage
-------------
$ ./scripts/export_to_markdown.py \
    records.json \
    output.md

Or, this can be used with `parallel` to bulk export a number of pages:

$ seq -w 00 18 | parallel -j4 -v "./scripts/export_to_markdown.py \
    database/proceedings/ismir20{}.json \
    ../ismir-home/docs/conferences/ismir20{}.md \
    --page_sort \
    --year 20{}"
"""
import argparse
import copy
import json
import os
import sys

TEMPLATE = '''
---
title: ISMIR {year}
---

## [Conferences]({{{{site.base_url}}}}/conferences) / ISMIR {year}

| Papers |
| --- |'''


def render_one(record):
    record = copy.deepcopy(record)
    record['html'] = record['zenodo'].get('html', '')
    record['pdf'] = record['ismir'].get('pdf', '')

    authors = ', '.join(record['author'])

    pages = record.pop('pages', '') + ' '

    return ('|{0}<br>**[{title}]({html})** {1}[[pdf]({pdf})]|'
            .format(authors, pages, **record))


def render(records, year=None, page_sort=False):
    if year is not None:
        records = filter(lambda x: x['year'] == year, records)

    if page_sort:
        records = sorted(records, key=lambda x: int(x.get('pages', '0').split('-')[0]))

    lines = [render_one(record) for record in records]
    return '\n'.join([TEMPLATE.format(year=year)] + lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("proceedings", type=str,
                        help="Path to proceedings records.")
    parser.add_argument("output_file", type=str,
                        help="Path to output markdown file.")
    parser.add_argument("--page_sort", dest="page_sort", action='store_true',
                        help="If given, sort records by page number.")
    parser.add_argument("--year", type=str, default=None,
                        help="Year of the conference records.")

    args = parser.parse_args()
    proceedings = json.load(open(args.proceedings))

    with open(args.output_file, 'w') as fp:
        fp.write(render(proceedings, page_sort=args.page_sort, year=args.year))

    sys.exit(0 if os.path.exists(args.output_file) else 1)
