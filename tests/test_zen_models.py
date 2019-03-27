import pytest

import zen.models


def test_Record():
    rec = zen.models.Record(foo='a', bar=1)
    assert rec['foo'] == 'a'
    assert rec['bar'] == 1


def test_Record_dropna():
    rec = zen.models.Record(foo=0, bar=False, baz=None)
    assert 'baz' not in rec.dropna()
    assert len(rec.dropna()) == 2


def test_DBLP():
    rec = zen.models.DBLP(author='a', title='b', year='1999')
    assert set(rec.keys()) == set(zen.models.DBLP.FIELDS)

    with pytest.raises(TypeError):
        zen.models.DBLP(creators='a', **rec)


def test_Zenodo():
    rec = zen.models.Zenodo(
        title='a', creators=[dict(name='foo')], partof_pages='1-3',
        conference_dates='24-27', conference_place='earth!',
        conference_title='whizbang', partof_title='proc of whizbang',
        publication_date='today', conference_acronym='WB',
        conference_url='http://baz.com', imprint_place='here',
        access_right='open', license='cc-by')
    assert set(rec.keys()) == set(zen.models.Zenodo.FIELDS)

    with pytest.raises(TypeError):
        zen.models.Zenodo(zenodo_id=14, **rec)


def test_IsmirPaper():
    rec = zen.models.IsmirPaper(
        title='baz', author='somebody', year='1234',
        doi='1.24/934', url='http://baz.com', ee='', pages='3-6')
    assert set(rec.keys()) == set(zen.models.IsmirPaper.FIELDS)

    with pytest.raises(TypeError):
        zen.models.Zenodo(creators=14, **rec)


def test_IsmirConference():
    rec = zen.models.IsmirConference(
        conference_dates='1-2', conference_place='earth', imprint_place='also earth',
        conference_title='foo bar', partof_title='proc of foo bar', publication_date='13 smarch',
        imprint_isbn='13478599123', conference_acronym='FB', conference_url='http://wee.com',
        imprint_publisher='blah', upload_type='publication', publication_type='paper',
        access_right='open', license='cc-by')

    assert set(rec.keys()) == set(zen.models.IsmirConference.FIELDS)

    with pytest.raises(TypeError):
        zen.models.IsmirConference(zenodo_id=12, **rec)


def test_merge():
    rec1 = zen.models.IsmirPaper(
        title='baz', author='somebody', year='1234',
        doi='1.24/934', url='http://baz.com', ee='', pages='3-6')
    rec2 = zen.models.IsmirConference(
        conference_dates='1-2', conference_place='earth', imprint_place='also earth',
        conference_title='foo bar', partof_title='proc of foo bar', publication_date='13 smarch',
        imprint_isbn='13478599123', conference_acronym='FB', conference_url='http://wee.com',
        imprint_publisher='blah', upload_type='publication', publication_type='paper',
        access_right='open', license='cc-by')
    result = zen.models.merge(
        zen.models.Zenodo, rec1, rec2, creators=[dict(name='blah')])

    assert set(result.keys()) == set(zen.models.Zenodo.FIELDS)
    assert result['title'] == 'baz'
    assert result['access_right'] == 'open'


def test_creators_to_author():
    creators = [dict(name='a'), dict(name='b')]
    assert zen.models.creators_to_author(creators) == ['a', 'b']
    assert zen.models.creators_to_author(creators[:1]) == 'a'


def test_author_to_creators():
    author = ['a', 'b']
    creators = [dict(name='a'), dict(name='b')]
    assert zen.models.author_to_creators(author) == creators
    assert zen.models.author_to_creators(author[0]) == creators[:1]
