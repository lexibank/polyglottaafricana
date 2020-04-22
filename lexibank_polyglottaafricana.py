from pathlib import Path

from clldutils.misc import slug

from pylexibank import FormSpec, Dataset as BaseDataset


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "polyglottaafricana"

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-"),  # characters that denote missing data.
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # We ignore all the plural forms
        replacements=[("ọ̄ ", "o˞ː ")],  # replacements with spaces
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """

        # Write source
        args.writer.add_sources()

        # Write languages
        language_map = args.writer.add_languages(lookup_factory="Name")

        # Write concepts
        cmap = args.writer.add_concepts(
            id_factory=lambda c: c.number + "_" + slug(c.gloss),
            lookup_factory=lambda c: c.gloss
        )

        # Write forms
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
                Source=["Koelle1854"],
            )
