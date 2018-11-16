# conference-archive
Tools for archiving conference proceedings, snapshots of metadata.


## What's going on here?

This repository consists of two different components:

- **Data**: Single source of ground truth for proceedings' metadata, citation records, and DOIs.
- **Tooling:** Software to index proceedings, interface with Zenodo, and convert metadata to markdown for display on the web (DBLP, ISMIR).

Implicit in this is the workflow for migrating proceedings and information for a
year's conference to the main trunk for posterity. At a high level, this looks like the following:

![](https://github.com/ismir/conference-archive/blob/master/img/proceedings-archive-flow.png)

Note that tracking this data in a standardized format makes it straightforward to update the metadata for these various consumers as bulk actions.

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


## JSON Database

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

