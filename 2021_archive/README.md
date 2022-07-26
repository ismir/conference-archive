# ISMIR 2021 Conference Archival

This readme explains the process of migrating proceedings and information for ISMIR 2021 conference to persistent web properties for posterity. Please look at https://github.com/ismir/conference-archive/blob/master/README.md to get an overall understanding of the workflow. 

For any questions about these scripts (2021 edition), please write to Ajay Srinivasamurthy at [ajays.murthy@upf.edu](mailto:ajays.murthy@upf.edu)

## Conference metadata
The conference metadata for ISMIR 2021 was generated manually and it has been added to https://github.com/ismir/conference-archive/blob/master/database/conferences.json This file is an input to the steps that follow. 

```json
   {
        "conference_dates": "November 7-12, 2021",
        "conference_place": "Online",
        "imprint_place": "Online",
        "conference_title": "International Society for Music Information Retrieval Conference",
        "partof_title": "Proceedings of the 22nd International Society for Music Information Retrieval Conference",
        "publication_date": "2021-11-07",
        "imprint_isbn": "978-1-7327299-0-2",
        "conference_acronym": "ISMIR 2021",
        "conference_url": "https://ismir2021.ismir.net",
        "imprint_publisher": "ISMIR",
        "upload_type": "publication",
        "publication_type": "conferencepaper",
        "access_right": "open",
        "license": "CC-BY-4.0"
    }
```

## Conference archival
It is assumed that you have used the [proceedings-builder](https://github.com/ismir/proceedings-builder) repository and successfully completed all the steps described for [2021 edition](https://github.com/ismir/proceedings-builder/blob/master/2021_scripts/README.md). We need the following files: 
1. A final JSON of proceedings metadata, generated using the proceedings builder. It will have the doi and url links empty, which will be added when we run the archiving tools below. In the scripts below, this input JSON is stored at `../temp_data/2021_input.json`
2. Set of final PDF files split from the full proceedings in a single folder, also generated using the proceedings builder. These files will be archived on Zenodo and a DOI will be assigned to each of them. In the steps below, this input folder with PDFs is assumed to be `../temp_data/split_articles/`.

### Step-1: Upload to ISMIR archives
While the official atchive of the papers is Zenodo, we also maintain an archive on [archives.ismir.net](archives.ismir.net) for historical reasons mostly. The PDFs are usually added with the filename template: https://archives.ismir.net/ismir<year>/paper/<paperID>.pdf  The path to the file in ISMIR archives is recorded in the metadata JSON at the key `"ee"` for each paper PDF, while the `"url"` key stores the path to the PDF in Zenodo. Please get in touch with the ISMIR board or the ISMIR tech team to add the files to the ISMIR archive. The complete proceedings PDF also needs to be added to the archive, e.g. [Full ISMIR 2021 proceedings PDF on ISMIR archive](http://archives.ismir.net/ismir2021/2021_Proceedings_ISMIR.pdf)

The following steps can use the PDF files from your local computer, e.g. `../temp_data/split_articles/` or from the ISMIR archives `https://archives.ismir.net/ismir<year>/paper/`, but will read the path to the PDF from the input metadata JSON (`../temp_data/2021_input.json`) using the `"ee"` key. So, please ensure the key points to the right path in the input JSON before running the following steps. 

### Step-2: Upload to Zenodo and generate DOI

The high level process is to upload each PDF to Zenodo using the Zenodo API and generate DOI for it. With the assigned DOI, we can update metadata JSON with the DOI and Zenodo URL to generate a final metadata JSOn complete in all respects. The final updated metadata JSON is then added to `../database/proceedings/2021.json` for posterity. 

The Zenodo archival is the most crucial step of the entire archival workflow and hence it's important to understand this process clearly. Please read the instructions on using the [Zenodo uploader](https://github.com/ismir/conference-archive/blob/master/README.md#3-zenodo-uploader) before procedding further. When you understand how upload works, try out with the sandbox version to familiarize yourself and check all metadata. 

```
# Test with a run like this
$ ../scripts/upload_to_zenodo.py \
    ../temp_data/2021_input.json \
    ../database/conferences.json \
    ../database/proceedings/2021.json \
    --stage dev \
    --verbose 50 \
    --num_cpus -2 \
    --max_items 2
```

Caveat: `upload_to_zenodo.py` is not very stable and please ensure you test it out thoroughly with a few files in `"dev"` before running it over the entire proceedings PDFs. These checks cannot be emphasized enough since we cannot delete the DOI once assigned in `"prod"` mode and it clutters up the Zenodo archive badly. 

Once tested, upload with `--stage prod` and `--max_items <num_papers_in_proceedings>`, which was 104 in ISMIR 2021. 

Check the output json updated with zenodo paths `../database/proceedings/2021.json` and commit it to the repo. 

Here is an example of a paper from ISMIR 2021 proceedings archived on Zenodo: https://zenodo.org/record/5625696#.Yt-eu-wzb_0

Follow the same process as a single paper, but manually upload the entire proceedings PDF to Zenodo as well and add the right tags, e.g. here is the final proceedings PDF archived on Zenodo: https://zenodo.org/record/5776687#.Yt-eAewzb_0

### Step-3: Export to Markdown/DBLP
Once proceedings have been uploaded to Zenodo (and the corresponding URLs have been generated), the proceedings metadata can be exported to markdown for serving on the web, e.g. DBLP, the ISMIR homepage, etc.

For the website, we need to generate [the proceedings markdown file](https://github.com/ismir/ismir-home/blob/master/docs/conferences/ismir2021.md) that will then produce the page [https://www.ismir.net/conferences/ismir2021.html](https://www.ismir.net/conferences/ismir2021.html). 

To do this, run, 
```
$ ../scripts/export_to_markdown.py \
    ../database/proceedings/2021.json \
    ismir2021.md
```
and then copy `ismir2021.md` to the target repository. Edit it to add an entry for the full proceedings PDF, e.g. as you see in https://www.ismir.net/conferences/ismir2021.html and any additional edits you see are needed. 
   
To generate DBLP metadata file to be added to DBLP database, you can run

```
$ ../scripts/generate_dblp.py \
    -y 2021 \ 
    ../database/conferences.json \ 
    ../database/proceedings/2021.json > ../database/proceedings/2021_dblp.html
    
```
### Step-4: Merge, Approve, Register
Please involve the ISMIR board or the ISMIR tech team to merge the markdown file to ISMIR web repo and to import `../database/proceedings/2021_dblp.html` into the DBLP database. Also work with the ISMIR board/tech team to approve the requests for the full proceedings PDF and each paper PDF that have been uploaded to Zenodo to be added to the ["ISMIR" community on Zenodo](https://zenodo.org/communities/ismir). Finally, work with the board/tech team to register the ISBN for the full conference proceedings. 

This completes the archival of proceedings for ISMIR 2021!
