"""Uploader demo for Zenodo.

To Use
------
You must set / export two environment variables for access to Zenodo;

```
export ZENODO_TOKEN_PROD=<PRIMARY_TOKEN>
export ZENODO_TOKEN_DEV=<SANDBOX_TOKEN>
```

Note: This script will yell loudly if the requested token is unset.

Now, you can then upload the sample data to the development site:
```
$ python scripts/uploader.py \
    data/sample_paper.pdf \
    data/sample_metadata.json \
    dev
```
"""
import argparse
import json
import logging
import sys
import zen

logger = logging.getLogger("demo_upload")


def upload(filename, metadata, stage, zid=None):
    """Upload a file / metadata pair to a Zenodo stage.

    Parameters
    ----------
    filename : str
        Path to a local file on disk.
        TODO: Could be a generic URI, to allow webscraping at the same time.

    metadata : dict
        Metadata associated with the resource.

    stage : str
        One of [dev, prod]; defines the deployment area to use.

    zid : str, default=None
        If provided, attempts to update the resource for the given Zenodo ID.

    Returns
    -------
    success : bool
        True on successful upload, otherwise False.
    """
    success = True
    if zid is None:
        zid = zen.create_id(stage=stage)

    success &= zen.upload_file(zid, filename, stage=stage)
    success &= zen.update_metadata(zid, metadata, stage=stage)
    success &= zen.publish(zid, stage=stage)
    logger.debug("Publishing: success={}".format(success))
    return success


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description=__doc__)

    # Inputs
    parser.add_argument("filename",
                        metavar="filename", type=str,
                        help="Path to a PDF file to upload.")
    parser.add_argument("metadata",
                        metavar="metadata", type=str,
                        help="Path to a JSON file of metadata to upload")
    parser.add_argument("stage",
                        metavar="stage", type=str,
                        help="Stage to execute.")
    args = parser.parse_args()

    metadata = json.load(open(args.metadata))
    success = upload(args.filename, metadata, args.stage)
    logging.info("Complete upload: success={}".format(success))
    sys.exit(0 if success else 1)
