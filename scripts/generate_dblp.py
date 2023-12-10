#!/usr/bin/python
import argparse
import json
import jinja2
import os


def main(year, conferences_json, proceedings_json, output_file):

    with open(conferences_json) as fp:
        conferences = json.load(fp)

    with open(proceedings_json) as fp:  # 'encoding' = 'utf-8' might need to be added based on the encoding
        proceedings = json.load(fp)

    if year is None:
        year = int(proceedings[0]['year'])

    if str(year) not in conferences:
        raise Exception(f"Year {year} isn't in conferences.json. Has it been added yet?")

    context = {
        'meta': conferences[str(year)],
        'year': year,
        'publications': proceedings
    }

    # get jinja template
    PATH = os.path.dirname(os.path.abspath(__file__))
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(PATH, 'templates')))

    template = template_env.get_template('dblp.xml')
    with open(output_file, 'w') as f:
        f.write(template.render(context))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a data file to be uploaded to DBLP")
    parser.add_argument("-y", required=False, type=int, help="The year to update for")
    parser.add_argument("conferences", help="path to conferences.json")
    parser.add_argument("papers", help="the 202x.json file with the proceedings")
    parser.add_argument("output_file", help="path to output XML file")

    args = parser.parse_args()
    main(args.y, args.conferences, args.papers, args.output_file)
