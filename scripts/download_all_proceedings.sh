#!/bin/bash

# Download the PDFs for all conferences
# Example call:
#   source download_all_proceedings.sh ../database/pdfs

for cur_year in {2000..2018}
do
    cmd="python download_proceedings.py ../database/proceedings/$cur_year.json $1"
    echo $cmd
    $cmd
done
