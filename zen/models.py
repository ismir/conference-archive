DEFAULT_DESCRIPTION = '[TODO] Add abstract here.'
DEFAULT_METADATA = {
    'license': 'CC-BY-4.0',
    'access_right': 'open',
    'description': DEFAULT_DESCRIPTION,
    'communities': [{'identifier': 'ismir'}],
    'imprint_publisher': 'ISMIR',
    'upload_type': 'publication',
    'publication_type': 'conferencepaper'
}


class DBLP(dict):
    '''DBLP paper entry'''
    FIELDS = ['author', 'title', 'year', 'booktitle', 'ee', 'crossref']

    def __init__(self, author, title, year, booktitle='ISMIR', ee='', crossref=''):
        super().__init__(author=author, title=title, year=year,
                         booktitle=booktitle, ee=ee, crossref=crossref)


class Zenodo(dict):
    '''Zenodo Metadata Object

    For more info, see the full documentation:
        http://developers.zenodo.org/#deposit-metadata
    '''
    FIELDS = ['upload_type', 'publication_type', 'title', 'creators', 'partof_pages',
              'description', 'communities', 'conference_dates', 'conference_place',
              'conference_title', 'partof_title', 'publication_date', 'conference_acronym',
              'conference_url', 'imprint_publisher', 'imprint_place', 'access_right',
              'license', 'doi']

    def __init__(self, upload_type, publication_type, title, creators, partof_pages,
                 description, communities, conference_dates, conference_place,
                 conference_title, partof_title, publication_date, conference_acronym,
                 conference_url, imprint_publisher, imprint_place, access_right, license,
                 doi=None):
        super().__init__(
            upload_type=upload_type, publication_type=publication_type,
            title=title, creators=creators, partof_pages=partof_pages,
            description=description, communities=communities, conference_dates=conference_dates,
            conference_place=conference_place, conference_title=conference_title,
            partof_title=partof_title, publication_date=publication_date,
            conference_acronym=conference_acronym, conference_url=conference_url,
            imprint_publisher=imprint_publisher, imprint_place=imprint_place,
            access_right=access_right, license=license, doi='')


class IsmirPaper(dict):
    '''ISMIR Paper Metadata Object'''

    FIELDS = ['title', 'author', 'year', 'doi', 'url', 'ee', 'abstract',
              'zenodo_id', 'dblp_key']

    def __init__(self, title, author, year, doi, url, ee, abstract='',
                 zenodo_id=None, dblp_key=None):
        super().__init__(title=title, author=author, year=year, doi=doi, url=url, ee=ee,
                         abstract=abstract, zenodo_id=zenodo_id, dblp_key=dblp_key)


class IsmirConference(dict):
    '''ISMIR Conference Metadata Object'''

    FIELDS = ['conference_dates', 'conference_place', 'imprint_place', 'conference_title',
              'partof_title', 'publication_date', 'imprint_isbn', 'conference_acronym',
              'conference_url', 'imprint_publisher', 'upload_type', 'publication_type',
              'access_right', 'license']

    def __init__(self, conference_dates, conference_place, imprint_place, conference_title,
                 partof_title, publication_date, imprint_isbn, conference_acronym,
                 conference_url, imprint_publisher, upload_type, publication_type,
                 access_right, license):
        super().__init__(
            conference_dates=conference_dates, conference_place=conference_place,
            imprint_place=imprint_place, conference_title=conference_title,
            partof_title=partof_title, publication_date=publication_date,
            imprint_isbn=imprint_isbn, conference_acronym=conference_acronym,
            conference_url=conference_url, imprint_publisher=imprint_publisher,
            upload_type=upload_type, publication_type=publication_type,
            access_right=access_right, license=license)


def merge(cls, *entities, **fields):
    '''Merge entities and project into a given data model.

    Parameters
    ----------
    cls : Entity type, subclass of dict
        Output entity to project into.

    *entities : iterable
        Entities to join, in descending order of importance.

    **fields : dict
        Key-value pairs to add.

    Returns
    -------
    obj : type(cls)
        Resulting object.
    '''

    accum = dict()
    for entity in entities[::-1]:
        accum.update(**entity)

    accum.update(**fields)
    return cls(**{k: accum.get(k) for k in cls.FIELDS})


def creators_to_author(creators):
    '''Transform Zenodo 'creators' to a string/list 'author'.

    Parameters
    ----------
    creators : list of dicts
        Collection of creator objects, keyed by name.

    Returns
    -------
    authors : str or list
        Collection of DBLP style authors.
    '''
    authors = [x['name'] for x in creators]
    if len(authors) == 1:
        authors = authors[0]

    return authors


def author_to_creators(authors):
    '''Transform DBLP 'authors' to Zenodo 'creators'.

    Parameters
    ----------
    authors : str or list
        Collection of DBLP style authors.

    Returns
    -------
    creators : list of dicts
        Collection of creator objects, keyed by name.
    '''
    if authors and isinstance(authors, str):
        authors = [authors]

    return [dict(name=_) for _ in authors]


def dblp_to_zenodo(record, conferences, abstract=DEFAULT_DESCRIPTION):
    """Format a DBLP record for Zenodo, backfilling the right conference meta.

    Parameters
    ----------
    record : dict
        Paper record from DBLP.

    conferences : dict
        Metadata corresponding to each conference, keyed by year (str).

    abstract : str
        Abstract for the corresponding paper.

    Returns
    -------
    meta : dict
        Appropriately formated metadata for Zenodo.
    """
    record = DBLP(**record)

    new_rec = dict(communities=[dict(identifier='ismir')])
    new_rec.update(**record.to_zenodo())

    # TODO: Conferences can only be keyed by strings...
    new_rec.update(**conferences[str(record['year'])])
    new_rec['creators'] = author_to_creators(new_rec.pop('author'))

    pages = new_rec.pop('pages', None)
    if pages:
        new_rec['partof_pages'] = pages

    if not new_rec.get('description'):
        new_rec['description'] = abstract

    return Zenodo(**new_rec)
