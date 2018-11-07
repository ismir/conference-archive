#!/usr/bin/env python
# coding: utf8
"""Extracts the abstracts from the proceedings PDFs.

Usage
-----

$ python ./scripts/extrac_pdf_abstract.py \
    ./path/to/pdfs

"""
import os
import glob
import io
import tempfile
import argparse
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
    pages = list(page_per_xobj(PdfReader(fname).pages, margin=0.5*72))

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

    abs_index = raw_text.find('ABSTRACT')
    intro_index = abs_index

    intro_index = raw_text.find('1. INTRODUCTION')

    if intro_index == -1:
        intro_index = raw_text.find('1.  INTRODUCTION')

    abstract = raw_text[abs_index + 8:intro_index]
    abstract = abstract.strip()

    # replace some ugly things
    abstract = abstract.replace('-\n', '')
    abstract = abstract.replace('\n', ' ')
    abstract = abstract.replace('ﬁ', 'fi')

    return abstract


def main(path_pdfs):
    """Main function which defines the processing pipeline."""

    # loop through all PDFs (could be parallized via joblib)
    for cur_fn_pdf in glob.glob(os.path.join(path_pdfs, '*.pdf')):
        path_tmp_pdf = extract_first_page(cur_fn_pdf)

        # extract all text from first page
        raw_text = extract_text(path_tmp_pdf)

        # extract abstract from whole page and replace hyphens etc.
        abstract = extract_abstract(raw_text)

        # clean up temp file
        os.remove(path_tmp_pdf)

        # TODO: Write to JSON
        print(repr(abstract))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument('path',
                        metavar='path', type=str,
                        help='Path to PDF versions of the papers.')
    args = parser.parse_args()

    main(args.path)
