from pathlib import Path

from clldutils.misc import slug

import pylexibank

# Customize your basic data.
# if you need to store other data in columns than the lexibank defaults,
# then over-ride the table type (pylexibank.[Language|Lexeme|Concept|Cognate|])
# and add the required columns e.g.
#
# import attr
#
# @attr.s
# class Concept(pylexibank.Concept):
#    MyAttribute1 = attr.ib(default=None)

BIB = """
@book{Koelle1854,
  address          = {London},
  author           = {Koelle, Sigismund W.},
  pages            = {216},
  publisher        = {Church Missionary House},
  title            = {Polyglotta Africana or Comparative Vocabulary of Nearly Three Hundred Words and Phrases in more than One Hundred Distinct African Languages},
  year             = {1854},
  besttxt          = {ptxt2\africa\koelle_polyglotta-africana1854_o.txt},
  fn               = {africa\koelle_polyglotta-africana1854.pdf, africa\koelle_polyglotta1854pages.pdf, africa\koelle_polyglotta-africana1854_o.pdf},
  hhtype           = {overview;wordlist}
}
"""


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "polyglottaafricana"

    # register custom data types here (or language_class,
    # lexeme_class, cognate_class):
    # concept_class = Concept

    # define the way in which forms should be handled
    form_spec = pylexibank.FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-"),  # characters that denote missing data.
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # We ignore all the plural forms
        replacements=[("ọ̄ ", "o˞ː ")],  # replacements with spaces
    )

    def cmd_download(self, args):
        """
        Download files to the raw/ directory. You can use helpers methods
        of `self.raw_dir`, e.g. to download a temporary TSV file and convert
        to persistent CSV:

        >>> with self.raw_dir.temp_download("http://www.example.com/e.tsv",
                "example.tsv") as data:
        ...     self.raw_dir.write_csv('template.csv',
        ...         self.raw_dir.read_csv(data, delimiter='\t'))
        """

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        A `pylexibank.cldf.LexibankWriter` instance is available as
        `args.writer`. Use the methods of this object to add data.
        """
        args.writer.add_sources(BIB)
        language_map = args.writer.add_languages(lookup_factory="Name")
        cmap = args.writer.add_concepts(
            id_factory=lambda c: slug(c.id), lookup_factory=lambda c: c.gloss
        )

        for row in self.raw_dir.read_csv(
            "test-koelle.csv", dicts=True, delimiter="\t"
        ):
            # Language name>--ethn>---Source name>----reflex.id>------
            # source.id>------page>---ORIGINAL FORM>--ORIGINAL TRANSLATION
            if row["ORIGINAL FORM"].strip().startswith("?"):
                # We ignore dubious forms, marked with a leading "?"
                continue
            args.writer.add_lexemes(
                Value=row["ORIGINAL FORM"],
                Language_ID=language_map[row["Language name"]],
                Parameter_ID=cmap[row["ORIGINAL TRANSLATION"]],
                Source="Koelle1854",
            )
