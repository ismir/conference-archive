# conference-archive
Machinery for archiving conference proceedings and maintaining metadata.

## Uploader

### To Use

You must set / export two environment variables for access to Zenodo;

```
export ZENODO_TOKEN_PROD=<PRIMARY_TOKEN>
export ZENODO_TOKEN_DEV=<SANDBOX_TOKEN>
```

To create / retrieve a token, proceed to Zenodo's developer [portal](https://zenodo.org/account/settings/applications/tokens/new/).


### Dev / Prod

Zenodo provides a [sandbox website](https://sandbox.zenodo.org) that is wholly disjoint from the [mainline service](https://sandbox.zenodo.org). We use the former for development and staging, and the latter for production.

