# External IMGT/IPD data

mhcgnomes uses facts derived from the IPD-IMGT/HLA and IPD-MHC databases, but its current tree does
not keep raw database snapshots and new releases do not bundle them. The providers apply their own
terms to copyrightable database content and explicitly discourage mirrors; see the pinned
[IPD-IMGT/HLA license](https://github.com/ANHIG/IMGTHLA/blob/b9e7356f990dc009fb71fcc540a3e7940a2ede49/LICENCE.md)
and [IPD-MHC license](https://github.com/ANHIG/IPDMHC/blob/127d27e22425f1e357d8ecd7795a9a637e82eb79/LICENCE.md).

The package still ships `mhcgnomes/data/allele_aliases.yaml`: this small, readable runtime index is
the maintained output of mhcgnomes' source-combination process, not a cache of the raw databases.
Its upstream releases and exact source hashes are recorded in `external_sources.json`. Encoding or
compressing upstream files would not change their provenance or redistribution terms, so releases
do not contain "obfuscated" source caches.

## Fetching maintained inputs

From a checkout or an installed package:

```bash
mhcgnomes-data
```

With no arguments, this fetches only the three inputs needed to regenerate `allele_aliases.yaml`.
Every source is pinned to an immutable commit in the provider's official repository and verified by
SHA-256 before use. Working copies go to `.external-data/`. Reusable content-addressed copies go
under `$XDG_CACHE_HOME/mhcgnomes/external-data-v1/` when that variable is set, or under
`~/.cache/mhcgnomes/external-data-v1/` otherwise.

Useful variants:

```bash
# Show all registered releases and purpose groups.
mhcgnomes-data --list

# Fetch inputs for exhaustive upstream compatibility validation.
mhcgnomes-data --group validation

# Preseed or consume a shared filesystem mirror, then forbid network fallback.
mhcgnomes-data --mirror /shared/mhcgnomes-data --offline

# Try organization caches before the official URLs.
mhcgnomes-data --mirror /shared/mhcgnomes-data \
  --mirror https://artifacts.example.org/mhcgnomes
```

`MHCGNOMES_DATA_CACHE` overrides the local content cache. `MHCGNOMES_DATA_MIRRORS` supplies a
semicolon-separated list of local directories or HTTP(S) base URLs. Resolution order is:

1. a checksum-valid file already in the destination;
2. the content-addressed local cache;
3. each configured local or HTTP(S) mirror in order;
4. the immutable official IPD/IMGT URL.

Invalid content is never accepted from any layer. `--offline` skips all network mirrors and the
official fallback. GitHub Actions uses the same content-addressed cache keyed by the manifest, so a
source is downloaded from the provider only when its pin changes or no valid CI cache exists.
Filesystem and HTTP(S) mirrors may expose each source by its manifest filename or SHA-256.

## Regenerating aliases

Run:

```bash
./mhcgnomes/data/combine_allele_aliases.sh
```

The script fetches missing inputs through the cache and combines:

- IPD-MHC 3.8.0.0 nomenclature history from `MHC.xml`;
- IPD-IMGT/HLA 3.42.0 allele history;
- IPD-IMGT/HLA 3.42.0 deleted-allele and suffix-change records; and
- `curated_allele_aliases.yaml`.

The official 3.42.0 `Deleted_alleles.txt` contains the suffix-change section, so no locally split
copy is needed. The historical IPD-MHC 3.5.0.1 XML remains registered for reproducibility, but it is
not an alias input: the old shell command repeated an argparse option, causing 3.8.0.0 to replace
3.5.0.1. Preserving only 3.8.0.0 keeps the generated runtime index byte-for-byte stable.

Exhaustive compatibility validation and the evaluation notebook use the optional protein inputs.
Fetch them first with `mhcgnomes-data --group validation`; they are read from
`.external-data/` and do not need copies in `tests/` or `evaluation/`. Run every official allele
name through the parser without generating or committing a transformed copy of the database:

```bash
mhcgnomes-validate-data
```

The normal test suite stays fully offline and contains a small explicit, accession-backed inventory
covering all 69 species prefixes in IPD-MHC 3.8.0.0. The cached CI job runs the exhaustive check.
