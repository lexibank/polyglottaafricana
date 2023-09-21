import itertools
import re
import string
import pathlib
import collections

from clldutils.misc import slug
from pyglottolog.references.roman import romanint

from pylexibank import Concept, FormSpec, Dataset as BaseDataset, progressbar, Lexeme, Language
import attr

PL_PATTERN = re.compile(r'[,;~]?\s+pl\.\s*')


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    RefLex_ID = attr.ib(
        default=None,
        metadata={
            'dc:description': 'Item ID in the RefLex database',
        }
    )
    Scan = attr.ib(
        default=None,
        metadata={
            'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#mediaReference',
        }
    )


@attr.s
class CustomLanguage(Language):
    RefLex_Name = attr.ib(
        default=None,
        metadata={
            'dc:description': 'Language name in RefLex',
        }
    )
    Ordinal = attr.ib(
        default=None,
        metadata={
            'datatype': 'integer',
            'dc:description': 'Ordinal derived from the multi-part language number in '
                              'Polyglotta Africana',
        }
    )
    Comment = attr.ib(
        default=None,
        metadata={
            'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#comment',
            'dc:description': "A comment regarding language identification, provided by Koelle's "
                              "informant for the language.",
        }
    )


def variety2ord(name):
    """
    Convert Koelle's multi-part variety numbers into a sortable tuple.
    """
    _, _, name = name.partition(' : ')
    lid, _, name = name.partition(' - ')
    comps = lid.split('-')
    part = romanint(comps.pop(0).lower())
    res = [part]
    if part in {2, 6, 11}:  # 2-a
        res.append(int(comps.pop(0)))
        if comps:
            res.append(ord(comps.pop(0)))
        else:
            res.append(999)
        res.append(999)
    else:  # A-1-a
        res.append(ord(comps.pop(0)))
        if part != 12:
            res.append(int(comps.pop(0)))
            if comps:
                res.append(ord(comps.pop(0)))
            else:
                res.append(999)
        else:  # A-a-2a
            third = comps.pop(0)
            res.append(ord(third) if third in 'ab' else int(third))
            if comps:
                fourth = comps.pop()
                res.append(ord(fourth) if fourth in string.ascii_lowercase else int(fourth[0]))
            else:
                res.append(999)
    assert not comps and len(res) == 4, lid
    res.append(name)
    return res


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "polyglottaafricana"
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    language_class = CustomLanguage

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=")~,&",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-"),  # characters that denote missing data.
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=False,
        replacements=[("ọ̄ ", "o˞ː ")],  # replacements with spaces
    )

    def _iter_variety_notes(self):
        lid_pattern = re.compile(r'Koelle 1854 : ([^\s]+) - [^\t]+\t')
        lid = None
        for line in self.raw_dir.read('koelle_variety_notes.txt').splitlines():
            m = lid_pattern.search(line)
            if m:
                lid = line[m.start():m.end() - 1]
            if 'Com:' in line:
                _, _, note = line.partition('Com:')
                yield (lid, note.strip())

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        args.writer.cldf.add_component(
            'MediaTable',
            {
                'name': 'SUBH_URL',
                'datatype': 'anyURI',
                'dc:description': 'URL of page in context of the scanned book',
            },
            {
                'name': 'Source',
                'separator': ';',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#source',
            },
        )

        args.writer.add_sources()

        # Write concepts
        concepts = collections.OrderedDict()
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
        cidx = {c: i for i, c in enumerate(concepts)}

        words = sorted(
            self.raw_dir.read_csv("test-koelle.csv", dicts=True, delimiter="\t"),
            key=lambda r: (cidx[r['ORIGINAL TRANSLATION']], variety2ord(r['Source name'])))
        for word in words:
            parts = PL_PATTERN.split(word['ORIGINAL FORM'], maxsplit=1)
            if len(parts) == 2:
                word['ORIGINAL FORM'] = parts[0].strip()
                word['plural'] = parts[1]

        reflex_name2gc = {r['Name']: r['Glottocode'] for r in self.languages}
        lid2comment = dict(self._iter_variety_notes())
        languages = {}
        for i, (lid, rows) in enumerate(itertools.groupby(
                sorted(words, key=lambda r: variety2ord(r['Source name'])),
                lambda r: r['Source name']), start=1):
            reflex_name = next(rows)['Language name']
            _, _, name = lid.partition(' : ')
            kid, _, name = name.partition(' - ')
            languages[lid] = kid
            args.writer.add_language(
                ID=kid,
                Name=name,
                Glottocode=reflex_name2gc.get(reflex_name),
                RefLex_Name=reflex_name,
                Ordinal=i,
                Comment=lid2comment.get(lid),
            )

        scans = set()
        for row in progressbar(words):
            # Language name>--ethn>---Source name>----reflex.id>------
            # source.id>------page>---ORIGINAL FORM>--ORIGINAL TRANSLATION
            if row["ORIGINAL FORM"].strip().startswith("?"):
                # We ignore dubious forms, marked with a leading "?"
                continue
            snumber = str(int(row['page']) + 40)
            if snumber not in scans:
                args.writer.objects['MediaTable'].append(dict(
                    ID=snumber,
                    Name=row['page'],
                    Description='',
                    Media_Type='image/tiff',
                    Download_URL='https://pic.sub.uni-hamburg.de/kitodo/PPN862704383/{}.tif'.format(
                        snumber.rjust(8, '0')),
                    SUBH_URL='https://resolver.sub.uni-hamburg.de/kitodo/PPN862704383/page/'
                             '{}'.format(snumber),
                    Source=['ScansHamburg'],
                ))
                scans.add(snumber)
            args.writer.add_lexemes(
                Value=row["ORIGINAL FORM"],
                Language_ID=languages[row["Source name"]],
                Parameter_ID=concepts[row["ORIGINAL TRANSLATION"]],
                Source=["Koelle1854"],
                Scan=snumber,
                RefLex_ID=row['reflex.id'],
                Comment=row.get('pural')
            )

        for l in args.writer.objects['LanguageTable']:
            if l['Latitude'] is None and l['Glottocode']:
                glang = args.glottolog.api.get_language(l['Glottocode'])
                if glang:
                    l['Latitude'] = glang.latitude
                    l['Longitude'] = glang.longitude
