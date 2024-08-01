# Releasing LSI

```shell
cldfbench lexibank.makecldf lexibank_polyglottaafricana.py --glottolog-version v5.0 --concepticon-version v3.2.0 --clts-version v2.3.0
pytest
```

```shell
cldfbench cldfreadme lexibank_polyglottaafricana.py
```

```shell
cldfbench cldfviz.map cldf --format svg --width 20 --output map.svg --with-ocean --language-properties Family
```

```shell
cldfbench cldfviz.erd --format compact.svg cldf > erd.svg
```

