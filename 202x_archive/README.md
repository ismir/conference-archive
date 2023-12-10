# ISMIR 202x Conference Archival

This readme explains the process of migrating proceedings and information for ISMIR 202x conference to persistent web properties for posterity. Please look at https://github.com/ismir/conference-archive/blob/master/README.md to get an overall understanding of the workflow.

For any questions about these scripts (202x edition), please write to Johan Pauwels at [j.pauwels@qmul.ac.uk](mailto:j.pauwels@qmul.ac.uk)

## Conference metadata
The conference metadata for ISMIR needs to be generated manually and added to https://github.com/ismir/conference-archive/blob/master/database/conferences.json This file is an input to the steps that follow.

```json
   {
        "conference_dates": "Month 1-31, 202x",
        "conference_place": "City, Country",
        "imprint_place": "City, country",
        "conference_title": "International Society for Music Information Retrieval Conference",
        "partof_title": "Proceedings of the Nth International Society for Music Information Retrieval Conference",
        "publication_date": "202x-mm-dd",
        "imprint_isbn": "978-1-7327299-3-3",
        "doi": "10.5281/zenodo.xxxxxxxx",
        "conference_acronym": "ISMIR 202x",
        "conference_url": "https://ismir202x.ismir.net",
        "imprint_publisher": "ISMIR",
        "upload_type": "publication",
        "publication_type": "conferencepaper",
        "access_right": "open",
        "license": "CC-BY-4.0",
        "editors": [
            "Some Person",
            "Another Person",
        ]
    }
```

## Conference archival
It is assumed that you have used the [proceedings-builder](https://github.com/ismir/proceedings-builder) repository and successfully completed all the steps described for [202x edition](https://github.com/ismir/proceedings-builder/blob/master/202x_scripts/README.md). We assume that the `proceeding-builder` repo is checked out in the same directory as this one, i.e. that its path is `../proceedings-builder` when in the root of this repo.

We need the following files:
1. A final JSON of proceedings metadata, generated using the proceedings builder. It will have the doi and url links empty, which will be added when we run the archiving tools below. In the scripts below, which need to be run from the root of this repo, this input JSON is stored at `../proceedings-builder/202x_Proceedings_ISMIR/metadata_final/202x_input.json`
2. Set of final PDF files split from the full proceedings in a single folder, also generated using the proceedings builder. These files will be archived on Zenodo and a DOI will be assigned to each of them. In the steps below, this input folder with PDFs is assumed to be `../proceedings-builder/202x_Proceedings_ISMIR/split_articles/`.

### Step-1: Upload to ISMIR archives
While the official archive of the papers is Zenodo, we also maintain an archive on [archives.ismir.net](archives.ismir.net) for historical reasons mostly and hosting during the conference. The PDFs are usually added with the filename template: `https://archives.ismir.net/ismir<year>/paper/<paperID>.pdf`. Please get in touch with the ISMIR board or the ISMIR tech team to add the files to the ISMIR archive. The complete proceedings PDF also needs to be added to the archive, e.g. [Full ISMIR 2021 proceedings PDF on ISMIR archive](http://archives.ismir.net/ismir2021/2021_Proceedings_ISMIR.pdf)

The following steps can use the PDF files from your local computer, e.g. `../proceedings-builder/202x_Proceedings_ISMIR/split_articles/` or from the ISMIR archives `https://archives.ismir.net/ismir<year>/paper/`, but will read the path to the PDF from the input metadata JSON (`../proceedings-builder/202x_Proceedings_ISMIR/metadata_final/202x.json`) using the `"ee"` key. So, please ensure the key points to the right path in the input JSON before running the following steps.

### Step-2: Upload to Zenodo and generate DOI

The high level process is to upload each PDF to Zenodo using the Zenodo API and generate a DOI for it. With the assigned DOI, we can update metadata JSON with the DOI and Zenodo URL to generate a final metadata JSON complete in all respects. The final updated metadata JSON is then added to `../database/proceedings/202x.json` for posterity.

The Zenodo archival is the most crucial step of the entire archival workflow and hence it's important to understand this process clearly. Please read the instructions on using the [Zenodo uploader](https://github.com/ismir/conference-archive/blob/master/README.md#3-zenodo-uploader) before proceeding further. When you understand how upload works, try out with the sandbox version to familiarize yourself and check all metadata.

```
# Test with a run like this
$ python ./scripts/upload_to_zenodo.py \
    ../proceedings-builder/202x_Proceedings_ISMIR/metadata_final/202x.json \
    database/conferences.json \
    database/proceedings/202x.json \
    --stage dev \
    --verbose 50 \
    --num_cpus -2 \
    --max_items 2
```

Caveat: `upload_to_zenodo.py` is not very stable and please ensure you test it out thoroughly with a few files in `"dev"` before running it over the entire proceedings PDFs. These checks cannot be emphasized enough since we cannot delete the DOI once assigned in `"prod"` mode and it clutters up the Zenodo archive badly.

Once tested, upload with `--stage prod` and remove `--max_items`.

Check the output json updated with zenodo paths `../database/proceedings/202x.json` and commit it to the repo.

Here is an example of a paper from ISMIR 2021 proceedings archived on Zenodo: https://zenodo.org/record/5625696#.Yt-eu-wzb_0

Follow the same process as a single paper, but manually upload the entire proceedings PDF to Zenodo as well and add the right tags, e.g. here is the final proceedings PDF archived on Zenodo: https://zenodo.org/record/5776687#.Yt-eAewzb_0

### Step-3: Export to Markdown/DBLP
Once proceedings have been uploaded to Zenodo (and the corresponding URLs have been generated), the proceedings metadata can be exported to markdown for serving on the web, e.g. DBLP, the ISMIR homepage, etc.

For the website, we need to generate [the proceedings markdown file](https://github.com/ismir/ismir-home/blob/master/docs/conferences/ismir2021.md) that will then produce the page [https://www.ismir.net/conferences/ismir2021.html](https://www.ismir.net/conferences/ismir2021.html).

To do this, run,
```
$ python ./scripts/export_to_markdown.py \
    ./database/proceedings/202x.json \
    ./database/conferences.json \
    ismir202x.md
```
and then copy `ismir202x.md` to the `ismir-home` repository.

To generate DBLP metadata file to be added to DBLP database, you can run

```
$ python ./scripts/generate_dblp.py \
    ./database/conferences.json \
    ./database/proceedings/202x.json \
    ./database/proceedings/202x_dblp.xml
```
The result is an XML file with [syntax as described on the DBLP site](https://dblp.org/faq/1474621.html).


### Step-4: Merge, Approve, Register

Send a pull request with the `ismir202x.md` to the [ISMIR website repo](https://github.com/jpauwels/ismir-home). Then send `database/proceedings/202x_dblp.xml` to Meinard Müller, who has a contact at DBLP to get the proceedings added. Finally, contact the ISMIR tech team who can add the full proceedings PDF and individual paper PDF on Zenodo to the ["ISMIR" community on Zenodo](https://zenodo.org/communities/ismir).

This completes the archival of proceedings for ISMIR!
