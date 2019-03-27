import pytest

import os
import shutil

import extract_pdf_abstract


def test_extract_pdf_abstract_extract_first_page(pdf_file, tmpdir):
    tmp_file = extract_pdf_abstract.extract_first_page(pdf_file)
    assert os.path.exists(tmp_file)
    shutil.copy(tmp_file, str(tmpdir))


def test_extract_pdf_abstract_extract_text(pdf_file, tmpdir):
    all_text = extract_pdf_abstract.extract_text(pdf_file)
    assert len(all_text) > 1000


def test_extract_pdf_abstract_extract_abstract():
    raw_text = 'foo barr ABSTRACT here\nis the abst-\nract 1. INTRODUCTION and the rest'
    abstract = extract_pdf_abstract.extract_abstract(raw_text)
    assert abstract == 'here is the abstract'
    assert extract_pdf_abstract.extract_abstract('there is no abstract') == ''


def test_extract_pdf_abstract_extract_extract():
    pass


def test_extract_pdf_abstract_main():
    pass


def test_extract_pdf_abstract_cli():
    pass
