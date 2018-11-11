
DROP_KEYS = ['ee', 'url', 'crossref', '@key', '@mdate', 'booktitle', 'year']
DEFAULT_DESCRIPTION = '[TODO] Add abstract here.'


class DBLP(dict):

    def __init__(self, author, title, year,
                 booktitle='ISMIR', ee='', url='', record_id=None, doi=''):
        super().__init__(author=author, title=title, year=year,
                         booktitle=booktitle, ee=ee, url=url,
                         record_id=record_id, doi=doi)


class Zenodo(dict):

    def __init__(self, record_id, title, creators, partof_pages,
                 description, communities,
                 conference_dates, conference_place, conference_title,
                 partof_title, publication_date, conference_acronym,
                 conference_url, imprint_publisher, imprint_place,
                 upload_type, publication_type, access_right, license):
        super().__init__(
            record_id=record_id, title=title, creators=creators, partof_pages=partof_pages,
            description=description, communities=communities, conference_dates=conference_dates,
            conference_place=conference_place, conference_title=conference_title,
            partof_title=partof_title, publication_date=publication_date,
            conference_acronym=conference_acronym, conference_url=conference_url,
            imprint_publisher=imprint_publisher, imprint_place=imprint_place,
            upload_type=upload_type, publication_type=publication_type,
            access_right=access_right, license=license)


def dblp_to_zenodo(record, conferences):
    """Format a DBLP record for Zenodo, backfilling the right conference meta.

    Parameters
    ----------
    record : dict
        Paper record from DBLP.

    conferences : dict
        Metadata corresponding to each conference, keyed by year (str).

    Returns
    -------
    meta : dict
        Appropriately formated metadata for Zenodo.
    """

    new_rec = dict(communities=[dict(identifier='ismir')])
    new_rec.update(**{k: v for k, v in record.items() if k not in DROP_KEYS})
    new_rec.update(**conferences[record['year']])
    authors = new_rec.pop('author')
    if authors and isinstance(authors, str):
        authors = [authors]

    new_rec['creators'] = [dict(name=_) for _ in authors]

    pages = new_rec.pop('pages', None)
    if pages:
        new_rec['partof_pages'] = pages

    if not new_rec.get('description'):
        new_rec['description'] = DEFAULT_DESCRIPTION

    return Zenodo(**new_rec)
