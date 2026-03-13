# mhcgnomes

`mhcgnomes` is a Python library and CLI for parsing MHC nomenclature across
human, model-organism, veterinary, and comparative immunogenetics datasets.

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

For local development, `./develop.sh` now installs the package with both dev
and docs dependencies so `mkdocs serve` works without extra setup.

## Python API

```python
import mhcgnomes

result = mhcgnomes.parse("HLA-A0201")
print(type(result).__name__)
print(result.to_string())
print(result.compact_string())
```

Expected output:

```text
Allele
HLA-A*02:01
A0201
```

## CLI

```bash
mhcgnomes "HLA-A*02:01" "DQ2.5"
python -m mhcgnomes --format json "HLA-A*02:01" "not a real allele"
```

The CLI reports:

- parsed result type
- normalized and compact forms
- species, gene, and MHC class where available
- structured `to_record()` fields for downstream inspection

Use `--strict` to fail fast on bad inputs instead of returning `ParseError`
rows.

## Docs In This Site

- `Curation Guide`: where new species, genes, aliases, and partial-source data
  should live
- `Immutable Data Objects`: the `3.0.0` object-model refactor and behavior
  compatibility notes

## Release Artifacts

GitHub releases now attach lightweight ontology exports so downstream tools can
inspect the curated runtime ontology without scraping YAML by hand.

Current release artifacts are:

- `mhcgnomes-species-ontology.csv`
- `mhcgnomes-gene-ontology.csv`

These are generated from the runtime ontology, not copied from a separate
shadow dataset.

## Local Docs Commands

```bash
./develop.sh
mkdocs serve
mkdocs build --strict
```

## Project Links

- Repository: <https://github.com/pirl-unc/mhcgnomes>
- PyPI: <https://pypi.org/project/mhcgnomes/>
- README: <https://github.com/pirl-unc/mhcgnomes/blob/main/README.md>
