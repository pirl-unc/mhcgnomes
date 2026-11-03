[![Tests](https://github.com/pirl-unc/mhcgnomes/actions/workflows/tests.yml/badge.svg)](https://github.com/pirl-unc/mhcgnomes/actions/workflows/tests.yml)
<a href="https://coveralls.io/github/pirl-unc/mhcgnomes">
<img src="https://coveralls.io/repos/github/pirl-unc/mhcgnomes/badge.svg?branch=main" alt="Coverage Status">
</a>
<a href="https://pypi.python.org/pypi/mhcgnomes/">
<img src="https://img.shields.io/pypi/v/mhcgnomes.svg?maxAge=1000" alt="PyPI" />
</a>
[![Docs](https://img.shields.io/badge/docs-pirl--unc.github.io%2Fmhcgnomes-blue)](https://pirl-unc.github.io/mhcgnomes/)

![](https://raw.githubusercontent.com/pirl-unc/mhcgnomes/main/gnome-red-text.png)

# mhcgnomes: Parsing MHC nomenclature in the wild

MHCgnomes is a parsing library for multi-species MHC nomenclature which
aims to correctly parse every name in [IEDB](http://www.iedb.org/), [IMGT/HLA](https://www.ebi.ac.uk/ipd/imgt/hla/), [IPD/MHC](https://www.ebi.ac.uk/ipd/mhc/), and the allele lists for both [NetMHCpan](https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1) and [NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0) predictors. This allows for standardization between immune databases and tools, which often use different naming conventions.

It is the allele-naming layer of the openvax stack:
[mhctools](https://github.com/openvax/mhctools),
[mhcflurry](https://github.com/openvax/mhcflurry) and
[mhcseqs](https://github.com/pirl-unc/mhcseqs) all normalize allele names
through it rather than parsing strings themselves.

## Install

```bash
pip install mhcgnomes
```

Requires Python 3.9 or later. There are no MHC data downloads: the curated
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
`compact_string()` the short one:

```python
>>> mhcgnomes.parse("HLA-A0201")
Allele(gene=Gene(species=Species(name='Homo sapiens', mhc_prefix='HLA'), name='A', mutations=()), allele_fields=('02', '01'), annotations=(), mutations=())
>>> mhcgnomes.parse("HLA-A0201").compact_string()
'A0201'
```

Pass `raise_on_error=False` to get `None` instead of a `ParseError`, and
`required_result_types=` to say which of those types you will accept. Both
matter when the input is not a curated allele list; see
[parsing untrusted input](https://pirl-unc.github.io/mhcgnomes/parsing/#parsing-untrusted-input).

## Command line

```bash
mhcgnomes "HLA-A*02:01" "DQ2.5"
```

This prints one row per input with the parsed result type, the normalized and
compact forms, species, gene, MHC class, and the parsed properties from
`to_record()`. `--format tsv` and `--format json` give machine-readable
output, `--strict` exits non-zero on the first parse error, and
`mhcgnomes data` manages the pinned external IMGT/IPD files. The
[command-line guide](https://pirl-unc.github.io/mhcgnomes/cli/) shows the full
output of each.

## Documentation

Full documentation: [pirl-unc.github.io/mhcgnomes](https://pirl-unc.github.io/mhcgnomes/).

- [MHC nomenclature in the wild](https://pirl-unc.github.io/mhcgnomes/nomenclature/): why one allele has a dozen spellings, and what the other named entities are
- [Parsing guide](https://pirl-unc.github.io/mhcgnomes/parsing/): result types, untrusted input, species inference, `species=` vs `default_species=`
- [Command line](https://pirl-unc.github.io/mhcgnomes/cli/)
- [Species and gene ontology](https://pirl-unc.github.io/mhcgnomes/species-ontology/): the species tree, prefix tiers and provenance, gene classes
- [Curation guide](https://pirl-unc.github.io/mhcgnomes/curation/): where new species, genes and aliases go
- [Immutable data objects](https://pirl-unc.github.io/mhcgnomes/immutable-data-objects/) and the [release process](https://pirl-unc.github.io/mhcgnomes/releasing/)

## Development

```bash
./develop.sh   # create .venv and install the package with dev and docs extras
./format.sh    # ruff format
./lint.sh      # ruff check and ruff format --check
./test.sh      # pytest with coverage, worker count capped by free RAM and CPUs
```

Every pull request bumps `mhcgnomes/version.py`; see the
[release process](https://pirl-unc.github.io/mhcgnomes/releasing/)
([source](https://github.com/pirl-unc/mhcgnomes/blob/main/docs/releasing.md)) for how a merged version reaches PyPI.

Raw IPD-IMGT/HLA and IPD-MHC snapshots are not committed or bundled in releases. See
[External IMGT/IPD data](https://github.com/pirl-unc/mhcgnomes/blob/main/EXTERNAL_DATA.md) for checksum-pinned downloads, local/CI caches,
optional mirrors, offline use, and alias regeneration.

To work on the documentation site:

```bash
./develop.sh
mkdocs serve
mkdocs build --strict
```

## License

[Apache License 2.0](https://github.com/pirl-unc/mhcgnomes/blob/main/LICENSE).
