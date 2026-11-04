# mhcgnomes

`mhcgnomes` is a Python library and CLI for parsing MHC nomenclature across
human, model-organism, veterinary, and comparative immunogenetics datasets.
It aims to correctly parse every name in [IEDB](http://www.iedb.org/),
[IMGT/HLA](https://www.ebi.ac.uk/ipd/imgt/hla/),
[IPD/MHC](https://www.ebi.ac.uk/ipd/mhc/), and the NetMHCpan and NetMHCIIpan
allele lists, so that databases and tools with different naming conventions
can be compared.

It is designed to normalize the strings you actually encounter in the wild:

- `HLA-A0201`
- `DQ2.5`
- `H2-Kk`
- `BoLA-NC11*001:01`
- `Sasa-DAB*01:01`

## Install

```bash
pip install mhcgnomes
```

Requires Python 3.11 or later. There are no MHC data downloads: the curated
species and gene ontology ships with the package.

## Quick start

```python
>>> import mhcgnomes
>>> [mhcgnomes.parse(s).to_string() for s in ["A*02:01", "HLA-A0201", "hla-a:02:01"]]
['HLA-A*02:01', 'HLA-A*02:01', 'HLA-A*02:01']
>>> mhcgnomes.parse("DQ2.5").to_string()
'HLA-DQA1*05:01/DQB1*02:01'
>>> type(mhcgnomes.parse("HLA-A2")).__name__
'Serotype'
>>> mhcgnomes.parse("H2-Kk").to_string()
'H2-K*k'
```

`parse` returns a structured object, not a string: an `Allele`, `Gene`,
`Pair`, `Serotype`, `Haplotype`, `MhcClass` or `Species`, depending on how much
the input actually specified. `to_string()` gives the normalized spelling and
`compact_string()` the short one.

## Where to go next

Roughly in reading order:

1. [MHC nomenclature in the wild](nomenclature.md): why one allele has a dozen
   spellings, what the suffixes mean, and which named entities are not alleles.
2. [Parsing guide](parsing.md): the result types and how they are ranked,
   restricting results for untrusted input, telling an explicit species from an
   inferred one, and `species=` versus `default_species=`.
3. [Command line](cli.md): parsing names from the shell, machine-readable
   output, and the pinned external data commands.
4. [Species and gene ontology](species-ontology.md): the curated YAML files,
   the species tree and what its edges mean, prefix tiers and provenance.
5. [Curation guide](curation.md): where new species, genes, aliases, and
   partial-source data should live.
6. [Immutable data objects](immutable-data-objects.md): the `3.0.0`
   object-model refactor and behavior compatibility notes.
7. [Species identity proposal](species-latin-name-scoping.md): make scientific
   name the canonical species key and treat prefixes/common names as aliases.
8. [Release process](releasing.md): how a merged version bump reaches PyPI.

## Local docs commands

```bash
./develop.sh
mkdocs serve
mkdocs build --strict
```

## Project links

- Repository: <https://github.com/pirl-unc/mhcgnomes>
- PyPI: <https://pypi.org/project/mhcgnomes/>
- README: <https://github.com/pirl-unc/mhcgnomes/blob/main/README.md>
