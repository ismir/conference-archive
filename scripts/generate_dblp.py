#!/usr/bin/python
import argparse
import json

import jinja2
import os


def main(year, conferences_json, proceedings_json):

    with open(conferences_json) as fp:
        conferences = json.load(fp)

    with open(proceedings_json) as fp:
        proceedings = json.load(fp)
        for p in proceedings:
            p["authors"] = ", ".join(p["author"])

    if year not in conferences:
        raise Exception(f"Year {year} isn't in conferences.json. Has it been added yet?")

    context = {
        'meta': conferences[year],
        'year': year,
        'publications': proceedings
    }

    # get jinja template
    PATH = os.path.dirname(os.path.abspath(__file__))
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')))

    template = template_env.get_template('dblp.txt')
    html = template.render(context)
    print(html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a data file to be uploaded to DBLP")
    parser.add_argument("-y", required=True, help="The year to update for")
    parser.add_argument("conferences", help="path to conferences.json")
    parser.add_argument("papers", help="the year.json file with the proceedings")

    args = parser.parse_args()
    main(args.y, args.conferences, args.papers)
