[![Tests](https://github.com/pirl-unc/mhcgnomes/actions/workflows/tests.yml/badge.svg)](https://github.com/pirl-unc/mhcgnomes/actions/workflows/tests.yml)
<a href="https://coveralls.io/github/pirl-unc/mhcgnomes">
<img src="https://coveralls.io/repos/github/pirl-unc/mhcgnomes/badge.svg?branch=main" alt="Coverage Status">
</a>
<a href="https://pypi.python.org/pypi/mhcgnomes/">
<img src="https://img.shields.io/pypi/v/mhcgnomes.svg?maxAge=1000" alt="PyPI" />
</a>

![](https://raw.githubusercontent.com/pirl-unc/mhcgnomes/main/gnome-red-text.png)

# mhcgnomes: Parsing MHC nomenclature in the wild

Documentation site: <https://pirl-unc.github.io/mhcgnomes/>

MHCgnomes is a parsing library for multi-species MHC nomenclature which
aims to correctly parse every name in [IEDB](http://www.iedb.org/), [IMGT/HLA](https://www.ebi.ac.uk/ipd/imgt/hla/), [IPD/MHC](https://www.ebi.ac.uk/ipd/mhc/), and the allele lists for both [NetMHCpan](https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1) and [NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0) predictors. This allows for standardization between immune databases and tools, which often use different naming conventions.

## Usage example

```python

In [1]: mhcgnomes.parse("HLA-A0201")
Out[1]: Allele(
    gene=Gene(
        species=Species(name="Homo sapiens", mhc_prefix="HLA"),
        name="A"),
    allele_fields=("02", "01"),
    annotations=(),
    mutations=())

In [2]: mhcgnomes.parse("HLA-A0201").to_string()
Out[2]: 'HLA-A*02:01'

In [3]: mhcgnomes.parse("HLA-A0201").compact_string()
Out[3]: 'A0201'

```

### Species-directed parsing

`species=` constrains parsing to a single species. The final parsed object
must match that species exactly, or parsing fails. This is useful when you
know the organism and want to reject cross-species mismatches:

```python
>>> mhcgnomes.parse("BoLA-DRB3*01:01", species="Bos taurus").to_string()
'Bota-DRB3*01:01'
>>> mhcgnomes.parse("HLA-A*02:01", species="Bos taurus", raise_on_error=False) is None
True
>>> mhcgnomes.parse("A*02:01", species="Homo sapiens").species.name
'Homo sapiens'
```

When the input uses an ancestor prefix (like `BoLA` for genus-level *Bos sp.*),
`species=` rewrites the result to the requested descendant species if valid.

`default_species=` is a less strict alternative — it provides a fallback
species hint for inputs that don't contain a species prefix, but does not
reject inputs that resolve to a different species:

```python
>>> mhcgnomes.parse("A*02:01", default_species="Homo sapiens").species.name
'Homo sapiens'
>>> mhcgnomes.parse("DMA", default_species="Chelonia mydas").species.name
'Chelonia mydas'
```

## CLI

After installation, a `mhcgnomes` CLI is available:

```bash
mhcgnomes "HLA-A*02:01" "DQ2.5"
# or:
python -m mhcgnomes "HLA-A*02:01" "DQ2.5"
```

This prints a table with:

- input string
- parsed result type
- normalized and compact forms
- species/gene/MHC class
- parsed properties from `to_record()`

You can also use machine-friendly output:

```bash
mhcgnomes --format tsv "HLA-A*02:01" "HLA-A2"
mhcgnomes --format json "HLA-A*02:01" "not a real allele"
```

By default, unparseable values are shown as `ParseError` rows.
Use strict mode to fail fast:

```bash
mhcgnomes --strict "not a real allele"
```

## The problem: MHC nomenclature is nuts

Despite the valiant efforts of groups such as the [Comparative MHC Nomenclature Committee](https://www.ebi.ac.uk/ipd/mhc/committee/), the names of MHC alleles you might encounter in different datasets (or accepted by immunoinformatics tools) are frustratingly ill specified. It's not uncommon to see dozens of different forms for the same allele.

For example, these all refer to the same MHC protein sequence:

- "HLA-A\*02:01"
- "HLA-A02:01"
- "HLA-A:02:01"
- "HLA-A0201"

Additionally, for human alleles, the species prefix is often omitted:

- "A\*02:01"
- "A\*0201"
- "A02:01"
- "A:02:01"
- "A0201"

### Annotations

Sometimes, alleles are bundled with modifier suffixes which specify
the functionality or abundance of the MHC. Here's an example with an allele
which is secreted instead of membrane-bound:

- "HLA-A\*02:01:01S"

These are collected in the `annotations` field of an
[`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
result.

Multi-letter annotations are also used in some non-human systems. In particular,
`Ps` (pseudogene) and `Sp` (splice variant) appear as suffixes on allele fields,
e.g. `Mamu-B*074:03Sp` or `Caja-B5*01:01Ps`, and are parsed into the
`annotations` field as `Sp` or `Ps` respectively.

Note that `Ps` can also appear as part of a gene name (prefix or suffix) in
non-human primates, such as `Caja-G2Ps*01`. In those cases `Ps` is treated as
part of the gene name, not an allele annotation.

### Mutations

MHC proteins are sometimes described in terms of mutations to a known allele.

- "HLA-B\*08:01 N80I mutant"

These mutations are collected in the `mutations` field of an
[`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) result.

### Beyond humans

To make things worse, several model organisms (like mice and rats) use archaic
naming systems, where there is no notion of allele groups or four/six/eight
digit alleles but every allele is simply given a name, such as:

- "H2-Kk"
- "RT1-9.5f"

In the above example "H2"/"RT1" correspond to species, "K"/"9.5" are
the gene names and "k"/"f" are the allele names.

To make these even worse, the name of a species is subject to variation (e.g. "H2" vs. "H-2") as well as drift over time (e.g. ChLA -> MhcPatr -> Patr).

### Serotypes, supertypes, haplotypes, and other named entities

Besides alleles there are also other named MHC related entities you'll encounter in immunological data. Closely related to alleles are serotypes, which effectively denote a grouping of alleles that are all recognized by the same antibody:

- "HLA-A2"
- "A2"

Supertypes are functional groupings based on shared peptide-binding specificity rather than serological reactivity (Sidney et al. 2008). These are parsed when the "supertype" keyword is present:

- "A2 supertype"
- "HLA-B44 supertype"

Class II heterodimers can be specified using dot notation, which is common in celiac disease literature:

- "DQ2.5" (equivalent to DQA1\*05:01/DQB1\*02:01)
- "DQ8.5"

In many datasets the exact allele is not known but an experiment might note the genetic background of a model animal, resulting in loose haplotype restrictions such as:

- "H2-k class I"

Yes, good luck disambiguating "H2-k" the haplotype from "H2-K" the gene, especially since capitalization is not stable enough to be relied on for parsing.

In some cases immunological data comes only with a denoted species (e.g. "mouse"), a gene (e.g. "HLA-A"), or an MHC class ("human class I"). MHCgnomes has a structured representation for all of these cases and more.

## Parsing strategy

It is a fool's errand to curate _all_ possible MHC allele names since that list grows daily as the MHC loci of more people (and non-human animals) are sequenced. Instead, MHCgnomes contains an ontology of curated species and genes and then attempts to parse any given string into a multiple candidates of the following types:

- [`Species`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/species.py)
- [`Gene`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/gene.py)
- [`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
- [`AlleleWithoutGene`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele_without_gene.py)
- [`Pair`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/pair.py)
- [`Class2Locus`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/class2_locus.py)
- [`MhcClass`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/mhc_class.py)
- [`Haplotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py)
- [`Serotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)
- [`Supertype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/supertype.py)

The set of candidate interpretations for each string are then
ranked according to heuristic rules. For example, a string will be
preferentially interpreted as an [`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) rather
than a [`Serotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)
or [`Haplotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py).

## How many digits per field?

Originally alleles for many genes were numbered with two digits:

- "HLA-MICB\*01"

But as the number of identified alleles increased, the number of
fields specifying a distinct protein increase to two. This became
conventionally called a "four digit" format, since each field has two
digits. Yet, as the number of identified alleles continued to increase, then
the number of digits per field has often increased from two to three:

- "MICB\*002:01"
- "HLA-A00201"
- "A:002:01"
- "A\*00201"

These are not always currently treated as equivalent to allele strings with two digits in their first field, but that feature is in the works.

However, if databases such as [IPD-MHC](https://www.ebi.ac.uk/ipd/mhc/) or [IMGT-HLA](https://www.ebi.ac.uk/ipd/imgt/hla/) recorded an older form of an allele, then MHCgnomes can optionally map it onto the modern version (including capturing differences in numbers of digits per field).

## Species and gene ontology

MHCgnomes maintains a curated ontology of species prefixes and MHC gene names
in YAML data files under `mhcgnomes/data/`. The key files are:

| File | Purpose |
| --- | --- |
| `species.yaml` | Canonical species entries with MHC prefix, gene names, and class assignments |
| `gene_aliases.yaml` | Alternative gene spellings that normalize to canonical genes |
| `allele_aliases.yaml` | Retired or shorthand allele names that normalize to canonical alleles |
| `known_alleles.yaml` | Curated known allele labels per species/gene |

### Species prefix conventions

Each species is identified by a short prefix (usually 2-4 characters) such as
`HLA` (human), `H2` (mouse), `Gaga` (chicken), or `Dare` (zebrafish). The
parser uses these prefixes to identify species before parsing gene names and
allele fields.

Prefixes are matched case-insensitively after stripping punctuation. A leading
`Mhc` prefix (common in bird MHC literature, e.g. `MhcTyal-DAB1*01:01`) is
automatically stripped as a fallback when normal prefix matching fails.

Some historically important prefixes are not single-species codes. Prefixes
such as `DLA`, `SLA`, `OLA`, `BoLA`, and `CELA` are curated as umbrella taxon
nodes in the ontology because the external nomenclature itself is genus- or
clade-level rather than species-specific. For example:

- `DLA` maps to `Canis sp.`, while `Calu` maps specifically to `Canis lupus`
- `SLA` maps to `Sus sp.`, while `Susc` maps specifically to `Sus scrofa`
- `BoLA` maps to `Bos sp.`, while `Bota` maps specifically to `Bos taurus`
- `OLA` maps to `Ovis sp.`, while `Ovar` maps specifically to `Ovis aries`
- `CELA` maps to `Cetacea sp.`, while `Tutr` maps specifically to `Tursiops truncatus`

This distinction matters when interpreting parsed objects: an allele parsed
from `BoLA-...` is attached to the generic cattle node unless the parse is
explicitly constrained or rewritten to a descendant species.

### MHC gene class assignments

Genes in `species.yaml` are organized by MHC class:

- **Ia**: Classical class I (associates with B2M, presents peptides)
- **Ib**: Non-classical class I (in MHC locus, associates with B2M)
- **Ic**: Related MHC locus genes, no B2M association (e.g. MICA)
- **Id**: Class I-related genes on other chromosomes
- **IIa**: Classical class II alpha/beta chains presenting peptides
- **IIb**: Accessory or non-classical class II proteins
- **other**: Antigen processing genes (TAP1, TAP2, TAPBP, B2M)

### Species prefix tiers

As mhcgnomes supports more species, short prefix codes increasingly collide.
One-letter codes like `HLA`/`SLA`/`DLA`, two-letter codes like `OrLA`, and
four-letter codes like `Calu` all hit collisions as coverage grows. We support
multiple prefix tiers so that every species is always parseable:

| Tier | Form | Example | When used |
| --- | --- | --- | --- |
| Established short prefix | 1–4 letters | `HLA`, `Gaga`, `Crpo` | Published in MHC literature or IPD-MHC. Preferred for display. |
| Novel 4+4 prefix | First 4 of genus + first 4 of species | `OryzLati`, `StruCame` | Standard display prefix for species without an established literature prefix. |
| 5+5 long prefix | First 5 of genus + first 5 of species | `HomoSapie`, `OryziLatip` | Auto-generated alias for all binomial species. Always parseable. |
| Full latin name | Concatenated genus + species | `HomoSapiens`, `ChrysemysPicta` | Always parseable as an alternative. Guaranteed collision-free. |

Legacy committee-style prefixes are not always at the same taxonomic level as
modern four-letter species prefixes. `DLA`, `SLA`, `OLA`, `BoLA`, and `CELA`
behave as generic umbrella prefixes for curated taxon nodes, while descendants
may also have their own species-specific prefixes such as `Calu`, `Susc`,
`Ovar`, `Bota`, or `Tutr`.

All tiers are parsed case-insensitively. For example, these all parse to the
same allele:

```
HLA-A*02:01          # established prefix
HomoSapi-A*02:01     # 4+4 novel prefix (auto-generated alias)
HomoSapie-A*02:01    # 5+5 long prefix (auto-generated alias)
HomoSapiens-A*02:01  # full latin name
Homo sapiens-A*02:01 # latin name with space
```

The 8-letter (4+4) novel prefix space greatly reduces collision probability compared to
4-letter codes, but only the full latin name is truly guaranteed to be unique.
Since we don't yet know what naming conventions the scientific community will
settle on for newer taxa, we support all tiers simultaneously.

**Which prefixes are established vs generated:** Comments in `species.yaml`
document which prefixes are attested in MHC literature and which were generated
by mhcgnomes. Established prefixes are never changed; generated prefixes are
subject to replacement if a community convention emerges.

See the [Curation Guide](https://pirl-unc.github.io/mhcgnomes/curation/) for
the full prefix conflict resolution policy ([source](docs/curation.md)).

## References

- [IPD-MHC: nomenclature requirements for the non-human major histocompatibility complex in the next-generation sequencing era](https://link.springer.com/article/10.1007%2Fs00251-018-1072-4)
- [Comparative MHC nomenclature: report from the ISAG/IUIS-VIC committee 2018]()
- [ISAG/IUIS-VIC Comparative MHC Nomenclature
  Committee report, 2005](https://link.springer.com/content/pdf/10.1007%2Fs00251-005-0071-4.pdf)
- [Marsupial MHC Class II β Genes Are Not Orthologous to the Eutherian β Gene Families]()
- [Nomenclature for factors of the SLA system, update 2008](https://www.ncbi.nlm.nih.gov/pubmed/19317739)

## Development

### Local docs

```bash
./develop.sh
mkdocs serve
mkdocs build --strict
```
