#!/usr/bin/env python
# coding: utf8
"""Extracts the abstracts and page numbers from the proceedings PDFs.

Usage
-----

$ python ./scripts/extract_pdf_abstract.py \
    ./path/to/proceedings/2017.json \
    ./path/to/pdfs

"""
import argparse
from joblib import Parallel, delayed
import json
import io
import os
import pdfminer.high_level
import pdfminer.layout
import pdfminer.settings
from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import page_per_xobj
import tempfile
import tqdm


pdfminer.settings.STRICT = False
MAX_LEN = 1500


def extract_first_page(fname):

    # create a temporary PDF file
    path_tmpfile = os.path.join(tempfile.gettempdir(), os.path.basename(fname))

    # extract all elements from the PDF and put them on separate pages
    pdf_reader = PdfReader(fname).pages
    pages = list(page_per_xobj(pdf_reader))

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

    # if no intro index was found, return empty abstract
    if intro_index == -1:
        return ''

    # post-processing
    abstract = raw_text[abs_index + len(query_abstract):intro_index]
    abstract = abstract.strip()

    # replace some ugly things
    abstract = abstract.replace('-\n', '')
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('ﬁ', 'fi')
    abstract = abstract.replace('ﬂ', 'fl')
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
    if len(abstract) > MAX_LEN:
        print('{}: Abstract is too long.'.format(path_pdf))

    if not abstract:
        print('{}: Could not extract abstract.'.format(path_pdf))

    # clean up temp file
    os.unlink(path_tmp_pdf)

    # TODO: Fix this return object
    out = {'@key': key, 'abstract': abstract}

    return out


def main(records, pdf_dir, num_cpus=-1, verbose=0):
    """Main function."""

    path_pdfs = []
    index_key = dict()

    for cur_idx, cur_record in enumerate(records):
        cur_key = cur_record['dblp_key']
        index_key[cur_key] = cur_idx
        cur_fn = cur_key.split('/')[-1]
        cur_path = os.path.join(pdf_dir, '{}.pdf'.format(cur_fn))
        path_pdfs.append((cur_key, cur_path))

    dfx = delayed(extract)
    pool = Parallel(n_jobs=num_cpus, verbose=verbose)
    abstracts = pool(dfx(cur_key, cur_path) for cur_key, cur_path in tqdm.tqdm(path_pdfs))

    out = {}

    for cur_abstract in abstracts:
        cur_record_idx = index_key[cur_abstract['@key']]
        records[cur_record_idx]['abstract'] = cur_abstract

    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument('metadata_file',
                        metavar='metadata_file', type=str,
                        help='JSON dump of metadata records.')
    parser.add_argument('pdf_dir',
                        metavar='metadata_file', type=str,
                        help='Path to conference PDFs.')
    parser.add_argument('--num_cpus',
                        metavar='num_cpus', type=int, default=-2,
                        help='Number of CPUs to use in parallel.')
    parser.add_argument('--verbose',
                        metavar='verbose', type=int, default=0,
                        help='Verbosity level for joblib.')
    args = parser.parse_args()

    with open(args.metadata_file, 'r') as fp:
        records = json.load(fp)

    proceedings_abstract = main(records, args.pdf_dir, args.num_cpus, args.verbose)

    with open(args.metadata_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(proceedings_abstract, indent=2))
