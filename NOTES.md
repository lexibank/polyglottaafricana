## Digitization

The digital data was obtained from the RefLex database (Reference Lexicon of Africa) edited by 
G. Ségérer (https://reflex.cnrs.fr/).


## Coverage

Polyglotta Africana covers almost 200 language varieties from 8 language families.

![](map.svg)


## Data model

See [cldf/README.md](cldf) for a description of the tables and columns and the
[entity-relationship diagram](erd.svg) for how they relate.

![](erd.svg)

Thus, displaying [words as listed in the book](https://resolver.sub.uni-hamburg.de/kitodo/PPN862704383/page/42) - i.e. 
with a concept as column and varieties as rows - can be done - for example using the tools of the 
[csvkit](https://csvkit.readthedocs.io/en/latest/) package - as follows:

```shell
$ csvjoin -c Language_ID,ID cldf/forms.csv cldf/languages.csv | csvgrep -c Parameter_ID -m 1_one | csvcut -c Language_ID,Name,Form,Segments | csvformat -T
Language_ID	Name	Form	Segments
I-A-1	Fúlup	fánọd	f á/a n o˞ d
I-A-2	Fī́lham	ánod	á/a n o d
I-B-1	Bṓla	pulólo	p u l ó/o l o
I-B-2	Sárār	pulálan·	p u l á/a l a n
I-B-3	Pẹ́pẹ̄l	olón·	o l ó/o n
I-B-3	Pẹ́pẹ̄l	olón·olón·	o l ó/o n o l ó/o n
I-B-3	Pẹ́pẹ̄l	púlon·	p ú/u l o n
I-B-4	Kányōp	púlọ̄́lẹ	p ú/u l o˞ː l e˞
...
```
