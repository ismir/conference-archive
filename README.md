# conference-archive
Tools for archiving conference proceedings, snapshots of metadata.


## What's going on here?

This repository consists of two different components:

- **Data**: Single source of ground truth for proceedings' metadata, citation records, and DOIs.
- **Tooling:** Software to index proceedings, interface with Zenodo, and convert metadata to markdown for display on the web (DBLP, ISMIR).

## JSON Databases

There are two types of database files maintained in this repository:

* Conference proceedings (one per conference)
* Conference metadata

### Conference Proceedings

The proceedings metadata of each conference contains an array of records conforming to the `IsmirPaper` entity type, defined in `zen.models`.

Each record looks like the following:

```json
{
  "author": "Susan Music",
  "title": "The first ISMIR paper",
  "year": "2000",
  "crossref": "conf/ismir/2000",
  "booktitle": "ISMIR",
  "ee": "https://zenodo.org/record/1416260/files/Music00.pdf",
  "url": "https://doi.org/10.5281/zenodo.1416260",
  "zenodo_id": 1416260,
  "dblp_key": "conf/ismir/MusicS00",
  "doi": "10.5281/zenodo.1416260",
  "abstract": "..."
}
```

### Conference metadata

The metadata for all conferences is contained in an object of records conforming to the `IsmirConference` entity type, defined in `zen.models`, keyed by year (as a `string`, because an `int` cannot be a key in a JSON object).

Each key-record pair looks like the following:

```json
{
  "2018":{
    "conference_dates": "September 23-27, 2018",
    "conference_place": "Paris, France",
    "imprint_place": "Paris, France",
    "conference_title": "International Society for Music Information Retrieval Conference",
    "partof_title": "Proceedings of the 19th International Society for Music Information Retrieval Conference",
    "publication_date": "2018-09-23",
    "imprint_isbn": "978-2-9540351-2-3",
    "conference_acronym": "ISMIR 2018",
    "conference_url": "http://ismir2018.ismir.net",
    "imprint_publisher": "ISMIR",
    "upload_type": "publication",
    "publication_type": "conferencepaper",
    "access_right": "open",
    "license": "CC-BY-4.0"
  }
  ...
}
```

## Workflow

This workflow aims to migrate proceedings and information for a year's conference to persistent web properties for posterity. At a high level, this looks like the following:

![](https://github.com/ismir/conference-archive/blob/master/img/proceedings-archive-flow.png)


### 1. Produce Databases

There are a mix of ways to produce the necessary data structures:

a. Parse proceedings metadata from the conference submission system, e.g. SoftConf
b. Crawl the conference website
c. Manual effort

In the future, these files could be more efficiently produced via the [proceedings-builder](https://github.com/ismir/proceedings-builder) repository.


### 2. Extract Abstracts

TODO[@stefan-balke?]


### 3. Zenodo Uploader

You must set / export two environment variables for access to Zenodo;

```bash
export ZENODO_TOKEN_PROD=<PRIMARY_TOKEN>
export ZENODO_TOKEN_DEV=<SANDBOX_TOKEN>
```

To create / retrieve a token, proceed to Zenodo's developer [portal](https://zenodo.org/account/settings/applications/tokens/new/).

Zenodo provides a [sandbox website](https://sandbox.zenodo.org) that is wholly disjoint from the [mainline service](https://sandbox.zenodo.org). We use the former for development and staging, and the latter for production.

This can be called via the following:

```bash
$ ./scripts/upload_to_zenodo.py \
    data/new-proceedings.json \
    data/conferences.json \
    --output_file updated-proceedings.json \
    --stage dev \
    --verbose 50 \
    --num_cpus -2 \
    --max_items 10
```

Note that when uploading to production, the output proceedings file should overwrite (update) the input. Specifying alternative output files is helpful for staging and testing that things behave as expected.


### 4. Export to Markdown

Once proceedings have been uploaded to Zenodo (and the corresponding URLs have been generated), the proceedings metadata can be exported to markdown for serving on the web, e.g. DBLP, the ISMIR homepage, etc.

```bash
$ ./scripts/export_to_markdown.py \
    updated-proceedings.json \
    proceedings.md
```

## Development

### Running Tests

After installing `py.test` and `pytest-cov`, run tests and check coverage locally.

```bash
$ PYTHONPATH=.:scripts py.test -vs tests --cov zen scripts
```
