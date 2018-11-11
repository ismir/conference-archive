#!/usr/bin/env python
"""Render conference metadata to markdown

Functionality to dump proceedings records to well-formatted metadata.

Example usage
-------------
$ ./scripts/metadata_to_markdown.py \
    records.json \
    output.md

Or, this can be used with `parallel` to bulk export a number of pages:

$ seq -w 00 17 | \
    parallel -j4 -v "./scripts/metadata_to_markdown.py \
        data/proceedings-20181003.json \
        proceedings/ismir20{}.md --year 20{}"
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

    return ('|{0}<br>**[{title}]({url})** [[pdf]({ee})]|'
            .format(authors, **record))


def render(records, year=None):
    if year is not None:
        records = filter(lambda x: x['year'] == year, records)

    records = sorted(records, key=lambda x: x['@key'])

    lines = [render_one(record) for record in records]
    return '\n'.join(TEMPLATE + lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("proceedings",
                        metavar="proceedings", type=str,
                        help="Path to proceedings records.")
    parser.add_argument("output_file",
                        metavar="output_file", type=str,
                        help="Path to output markdown file.")
    parser.add_argument("--year",
                        metavar="year", type=str, default=None,
                        help="Year filter for records")

    args = parser.parse_args()
    proceedings = json.load(open(args.proceedings))

    with open(args.output_file, 'w') as fp:
        fp.write(render(proceedings.values(), year=args.year))

    sys.exit(0 if os.path.exists(args.output_file) else 1)
