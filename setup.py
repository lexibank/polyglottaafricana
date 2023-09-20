from setuptools import setup
import json


with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_polyglottaafricana",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_polyglottaafricana"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["polyglottaafricana=lexibank_polyglottaafricana:Dataset"]},
    install_requires=["cldfbench>=1.14", "pylexibank>=3.0"],
    extras_require={"test": ["pytest-cldf"]},
)
