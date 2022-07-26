#!/usr/bin/env python
"""Render conference metadata to markdown

Functionality to export proceedings records to markdown.

Example usage
-------------
$ ./scripts/export_to_markdown.py \
    records.json \
    output.md

Or, this can be used with `parallel` to bulk export a number of pages:

$ seq -w 00 18 | \
    parallel -j4 -v "./scripts/metadata_to_markdown.py \
        database/proceedings/2018.json \
        assets/md/ismir20{}.md --page_sort"
"""
import argparse
import copy
import json
import os
import sys

TEMPLATE = '''
---
title: Conferences
---

## [Conferences](/conferences) / ISMIR {year}

| Papers |
| --- |
'''


def render_one(record):
    record = copy.deepcopy(record)
    record['url'] = record.get('url', '')
    record['ee'] = record.get('ee', '')

    if isinstance(record['author'], list):
        authors = ', '.join(record['author'])
    else:
        authors = record['author']

    pages = record.pop('pages', '') + ' '

    return ('|{0}<br>**[{title}]({url})** {1}[[pdf]({ee})]|'
            .format(authors, pages, **record))


def render(records, year=None, page_sort=False):
    if year is not None:
        records = filter(lambda x: x['year'] == year, records)

    if page_sort:
        records = sorted(records, key=lambda x: int(x['pages'].split('-')[0]))

    lines = [render_one(record) for record in records]
    return '\n'.join([TEMPLATE] + lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("proceedings", type=str,
                        help="Path to proceedings records.")
    parser.add_argument("output_file", type=str,
                        help="Path to output markdown file.")
    parser.add_argument("--page_sort", dest="page_sort", action='store_true',
                        help="Path to output markdown file.")

    args = parser.parse_args()
    proceedings = json.load(open(args.proceedings)) # 'encoding' = 'utf-8' might need to be added based on the encoding

    with open(args.output_file, 'w') as fp:
        fp.write(render(proceedings, page_sort=args.page_sort))

    sys.exit(0 if os.path.exists(args.output_file) else 1)
