# Releasing Polyglotta Africana

```shell
git clone https://github.com/lexibank/polyglottaafricana polyglottaafricana-cldf
cd polyglottaafricana-cldf
pip install -e .[test]
```

```shell
cldfbench lexibank.makecldf lexibank_polyglottaafricana.py --glottolog-version v5.3 --concepticon-version v3.4.0 --clts-version v2.3.0
pytest
```

```shell
cldfbench cldfreadme lexibank_polyglottaafricana.py
```

```shell
pip install cldfviz[cartopy]
cldfbench cldfviz.map cldf --format svg --width 20 --output map.svg --with-ocean --language-properties Family
```

```shell
cldfbench cldfviz.erd --format compact.svg cldf > erd.svg
```
