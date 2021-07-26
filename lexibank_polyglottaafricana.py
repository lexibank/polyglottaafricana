from pathlib import Path

from clldutils.misc import slug

from pylexibank import Concept, FormSpec, Dataset as BaseDataset, progressbar
import attr


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "polyglottaafricana"
    concept_class = CustomConcept

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
        languages = args.writer.add_languages(lookup_factory="Name")

        # Write concepts
        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            idx = concept.number + "_" + slug(concept.english)
            for gloss in concept.attributes["lexibank_gloss"]:
                concepts[gloss.strip()] = idx
            concepts[concept.english] = idx
            args.writer.add_concept(
                ID=idx,
                Number=concept.number,
                Name=concept.english,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )

        # Write forms
        missing = set()
        for row in progressbar(
            self.raw_dir.read_csv("test-koelle.csv", dicts=True, delimiter="\t")
        ):
            # Language name>--ethn>---Source name>----reflex.id>------
            # source.id>------page>---ORIGINAL FORM>--ORIGINAL TRANSLATION
            if row["ORIGINAL FORM"].strip().startswith("?"):
                # We ignore dubious forms, marked with a leading "?"
                continue
            if row["ORIGINAL TRANSLATION"] in concepts:
                args.writer.add_lexemes(
                    Value=row["ORIGINAL FORM"],
                    Language_ID=languages[row["Language name"]],
                    Parameter_ID=concepts[row["ORIGINAL TRANSLATION"]],
                    Source=["Koelle1854"],
                )
            else:
                missing.add(row["ORIGINAL TRANSLATION"])
        for m in missing:
            print(m)
