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
import json
from pathlib import Path
import jinja2


def render(records, conferences, year=None, page_sort=False):
    if year is not None:
        records = filter(lambda x: x['year'] == str(year), records)
    else:
        year = int(records[0]['year'])

    if page_sort:
        records = sorted(records, key=lambda x: int(x['pages'].split('-')[0]))

    PATH = Path(__file__).absolute().parent
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(PATH / 'templates'))

    template = template_env.get_template('ismir_proceedings.md')
    context = {
        'meta': conferences[str(year)],
        'year': year,
        'publications': records
    }
    return template.render(context)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("proceedings", type=str,
                        help="Path to proceedings records.")
    parser.add_argument("conferences", type=str,
                        help="Path to conferences.json.")
    parser.add_argument("output_file", type=str,
                        help="Path to output markdown file.")
    parser.add_argument("--page_sort", dest="page_sort", action='store_true',
                        help="Sort records following page numbers.")

    args = parser.parse_args()
    with open(args.proceedings) as f:
        proceedings = json.load(f)
    with open(args.conferences) as f:
        conferences = json.load(f)

    with open(args.output_file, 'w') as fp:
        fp.write(render(proceedings, conferences, page_sort=args.page_sort))
