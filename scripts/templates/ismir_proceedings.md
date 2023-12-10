---
title: ISMIR {{ year }}
---

## [Conferences](/conferences) / ISMIR {{ year }}

**Full Proceedings**

**[{{ meta.partof_title}}](https://doi.org/{{ meta.doi }})**, {{ meta.conference_place }}, {{ meta.conference_dates }} (ISBN: {{ meta.imprint_isbn }}) [[pdf](https://zenodo.org/record/{{ meta.doi.split('.')[-1] }}/files/{{ year }}_Proceedings_ISMIR.pdf)]

| Papers |
| --- |
{%- for publication in publications %}
|{{ publication.author|join(", ") }}<br>**[{{ publication.title }}]({{ publication.url }})** {{ publication.pages }}[[pdf]({{ publication.ee }})]|
{%- endfor %}
