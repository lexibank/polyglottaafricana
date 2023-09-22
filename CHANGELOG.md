# Changes

## [v2.0]

We now use Koelle's original 200 language varieties as reference. Mapping to RefLex languages is
still possible using the RefLex language names given in the LanguageTable:

```shell
$ csvstat -c ID,RefLex_Name cldf/languages.csv 
  1. "ID"

	Type of data:          Text
	Contains null values:  False
	Unique values:         200
	Most common values:    I-A-1 (1x)
	                       I-A-2 (1x)
	                       I-B-1 (1x)
	                       I-B-2 (1x)
	                       I-B-3 (1x)

 10. "RefLex_Name"

	Type of data:          Text
	Contains null values:  False
	Unique values:         159
	Most common values:    Yoruba (10x)
	                       Igbo (5x)
	                       Mungaka (5x)
	                       Nde (4x)
	                       Mandinka (3x)

Row count: 200
```


## [v1.x]

Polyglotta Africana, as mapped to languages in the RefLex database.
