# conference-archive
Tools for archiving conference proceedings, snapshots of metadata.


## What's going on here?

This repository consists of two different components:

- **Tooling:** Software to index proceedings, extract metadata, and interface with Zenodo.
- **Data**: Single source of ground truth for proceedings' metadata, citation records, and DOIs.

Implicit in this is the workflow for migrating proceedings and information for a
year's conference to the main trunk for posterity. Documentation and diagrams to follow.

Note that tracking this data in a standardized format makes it straightforward to update the metadata on Zenodo for many papers in a bulk action.


## Tools

### Zenodo Uploader

#### To Use

You must set / export two environment variables for access to Zenodo;

```bash
export ZENODO_TOKEN_PROD=<PRIMARY_TOKEN>
export ZENODO_TOKEN_DEV=<SANDBOX_TOKEN>
```

To create / retrieve a token, proceed to Zenodo's developer [portal](https://zenodo.org/account/settings/applications/tokens/new/).


#### Dev / Prod

Zenodo provides a [sandbox website](https://sandbox.zenodo.org) that is wholly disjoint from the [mainline service](https://sandbox.zenodo.org). We use the former for development and staging, and the latter for production.


## Data

### Conference Proceedings

The proceedings of each conference is maintained a single JSON file, e.g. database, keyed by a deterministic hash of the year and authors surnames.

Each record looks like the following:

```
"proceedings":
  "key": {
    "author": "David Bainbridge",
    "title": "The role of Music IR in the New Zealand Digital Music Library project.",
    "year": "2000",
    "crossref": "conf/ismir/2000",
    "booktitle": "ISMIR",
    "ee": "https://zenodo.org/record/1416260/files/Bainbridge00.pdf",
    "url": "https://doi.org/10.5281/zenodo.1416260",
    "record_id": 1416260,
    "doi": "10.5281/zenodo.1416260"
  },
  ...
"conference":
  "conference_dates": "October 23-25, 2000",
  "conference_place": "Plymouth, United States",
  "conference_title": "Proceedings of the 1st International Symposium on Music Information Retrieval",
  "partof_title": "Proceedings of the 1st International Symposium on Music Information Retrieval",
  "publication_date": "2000-10-23",
  "conference_acronym": "ISMIR 2000",
  "conference_url": "http://ismir2000.ismir.net",
  "imprint_publisher": "ISMIR",
  "imprint_place": "Plymouth, United States",
  "upload_type": "publication",
  "publication_type": "conferencepaper",
  "access_right": "open",
  "license": "other-nc"
}
```