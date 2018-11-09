#!/usr/bin/env python
# coding: utf8
"""Extracts the abstracts from the proceedings PDFs.

Usage
-----

$ python ./scripts/extract_pdf_abstract.py \
    ./path/to/proceedings.json \
    ./path/to/pdfs \
    ./path/to/abstracts.json

"""
import os
import json
import warnings
import io
import tempfile
import argparse
import tqdm
from joblib import Parallel, delayed
import pdfminer.high_level
import pdfminer.layout
import pdfminer.settings
from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import page_per_xobj
pdfminer.settings.STRICT = False


def extract_first_page(fname):

    # create a temporary PDF file
    path_tmpfile = os.path.join(tempfile.gettempdir(), os.path.basename(fname))

    # extract all elements from the PDF and put them on separate pages
    pages = list(page_per_xobj(PdfReader(fname).pages))

    # write to temp file
    writer = PdfWriter(path_tmpfile)
    writer.addpages(pages)
    writer.write()

    return path_tmpfile


def extract_text(fname):
    """Get all the text from the PDF."""

    laparams = pdfminer.layout.LAParams()
    for param in ('all_texts', 'detect_vertical', 'word_margin', 'char_margin', 'line_margin', 'boxes_flow'):
        paramv = locals().get(param, None)
        if paramv is not None:
            setattr(laparams, param, paramv)

    # send output to a string stream
    outfp = io.StringIO()

    with open(fname, 'rb') as fp:
        pdfminer.high_level.extract_text_to_fp(fp, outfp=outfp, codec='utf-8',
                                               laparams=laparams, pages=0)

    return outfp.getvalue()


def extract_abstract(raw_text):
    """Search in the text for keywords and extract text in between."""

    query_abstract = 'ABSTRACT'
    abs_index = raw_text.find(query_abstract)
    intro_index = abs_index

    query_intro = '1. INTRODUCTION'
    intro_index = raw_text.find(query_intro)

    if intro_index == -1:
        intro_index = raw_text.find('1.  INTRODUCTION')

    try:
        # if no intro index was found, return empty abstract
        assert intro_index != -1
    except AssertionError:
        return ''

    # post-processing
    abstract = raw_text[abs_index + len(query_abstract):intro_index]
    abstract = abstract.strip()

    # replace some ugly things
    abstract = abstract.replace('-\n', '')
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('ﬁ', 'fi')
    abstract = abstract.replace('  ', ' ')

    return abstract


def extract(key, path_pdf):
    """Extraction function which defines the processing pipeline."""

    path_tmp_pdf = extract_first_page(path_pdf)

    # extract all text from first page
    raw_text = extract_text(path_tmp_pdf)

    # extract abstract from whole page and replace hyphens etc.
    abstract = extract_abstract(raw_text)

    # something went wrong when abstract is longer than 1500 chars
    if len(abstract) > 1500:
        print('{}: Abstract is too long.'.format(path_pdf))

    if not abstract:
        print('{}: Could not extract abstract.'.format(path_pdf))

    # clean up temp file
    os.remove(path_tmp_pdf)

    out = {'@key': key, 'abstract': abstract}

    return out


def main(records, pdf_dir, output_dir, num_cpus=-1, verbose=0):
    """Main function."""

    path_pdfs = []

    for cur_key in records.keys():
        cur_fn = cur_key.split('/')[-1]
        cur_path = os.path.join(pdf_dir, '{}.pdf'.format(cur_fn))
        path_pdfs.append((cur_key, cur_path))

    dfx = delayed(extract)
    pool = Parallel(n_jobs=num_cpus, verbose=verbose)
    abstracts = pool(dfx(cur_key, cur_path) for cur_key, cur_path in tqdm.tqdm(path_pdfs))

    out = {}

    for cur_abstract in abstracts:
        out[cur_abstract['@key']] = cur_abstract

    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument('metadata_file',
                        metavar='metadata_file', type=str,
                        help='JSON dump of metadata records.')
    parser.add_argument('pdf_dir',
                        metavar='metadata_file', type=str,
                        help='Path to conference PDFs.')
    parser.add_argument('output',
                        metavar='output', type=str,
                        help='Path to write the extracted abstracts.')
    parser.add_argument('--num_cpus',
                        metavar='num_cpus', type=int, default=-2,
                        help='Number of CPUs to use in parallel.')
    parser.add_argument('--verbose',
                        metavar='verbose', type=int, default=0,
                        help='Verbosity level for joblib.')
    args = parser.parse_args()

    with open(args.metadata_file, 'r') as fp:
        records = json.load(fp)

    abstracts = main(records, args.pdf_dir, args.output, args.num_cpus, args.verbose)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(json.dumps(abstracts, indent=2))
