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
mhcgnomes data
```

This lists all registered sources, releases, and purpose groups without accessing the network. The
explicit equivalent is `mhcgnomes data list`.

Download the three default inputs needed to regenerate `allele_aliases.yaml` with:

```bash
mhcgnomes data download
```

Source selection, destination, cache, mirror, and offline options belong to the `download`
subcommand; run `mhcgnomes data download --help` for the complete interface.

Every source is pinned to an immutable commit in the provider's official repository and verified
by SHA-256 before use. Working copies go to `.external-data/`. Reusable content-addressed copies
go under `$XDG_CACHE_HOME/mhcgnomes/external-data-v1/` when that variable is set, or under
`~/.cache/mhcgnomes/external-data-v1/` otherwise.

Useful variants:

```bash
# Show all registered releases and purpose groups.
mhcgnomes data list

# Fetch inputs for exhaustive upstream compatibility validation.
mhcgnomes data download --group validation

# Preseed or consume a shared filesystem mirror, then forbid network fallback.
mhcgnomes data download --mirror /shared/mhcgnomes-data --offline

# Try organization caches before the official URLs.
mhcgnomes data download --mirror /shared/mhcgnomes-data \
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
./scripts/combine_allele_aliases.sh
```

The script fetches missing inputs through the cache and combines:

- IPD-MHC 3.17.0.0 nomenclature history from `MHC.xml`;
- IPD-IMGT/HLA 3.66.0 allele history;
- IPD-IMGT/HLA 3.66.0 deleted-allele and suffix-change records; and
- `curated_allele_aliases.yaml`.

The official 3.66.0 `Deleted_alleles.txt` contains the suffix-change section, so no locally split
copy is needed. Historical IPD-MHC 3.5.0.1 and 3.8.0.0 XMLs remain registered under the `legacy`
group for reproducibility; the maintained non-human source is 3.17.0.0.

Exhaustive compatibility validation and the evaluation notebook use the optional protein inputs.
Fetch them first with `mhcgnomes data download --group validation`; they are read from
`.external-data/` and do not need copies in `tests/` or `evaluation/`. Run every official allele
name through the parser without generating or committing a transformed copy of the database:

```bash
mhcgnomes data validate
```

It accepts optional FASTA paths (default `.external-data/hla_prot.fasta` and
`.external-data/MHC_prot.fasta`) and `--max-failures`.

The normal test suite stays fully offline and contains a small explicit, accession-backed inventory
covering all 87 species prefixes in IPD-MHC 3.17.0.0. The cached CI job runs the exhaustive check.

## Source precedence and audit API

The generator reads IPD-MHC history from
`additional_fields/field[@name="nomenclature"]`, including comma-separated names.
Missing history fields fail regeneration instead of silently dropping a source.
HLA history and deletions are pinned to release 3.66.0 at immutable commit
`b2055ea33ef464781b9e8ecab20b275b6704f878` (see the manifest for URLs/checksums).
The deletion reader uses accession identity for suffix reversals and explicit
rename/equality clauses for deleted accessions; it does not infer sequence identity
from a later resubmission mentioned in prose.

Exact latest recorded names, including retained abandoned records, win over all redirects. Curated evidence wins over automatic
history. Conflicting automatic targets are excluded; targets differing only by
additional colon-separated fields select the longest supported target for a
renamed legacy key. A spelling that is only a shorter colon-delimited prefix of
its target is not redirected: history must not silently choose a more specific
member of a partial name. Cycles fail
regeneration. Historical bare names are excluded unless curated: they can name
loci or haplotypes, so `Mamu-B17` remains a locus. Aliases remain opt-in.

`data-sources/allele-alias-audit.json` records source coverage, decision counts,
excluded/conflicting mappings and unresolved deletion descriptions. Each emitted
alias cites its source filename and accession beside the data. The generated
`current_allele_names.yaml` is a sparse precedence guard: it includes current names
sharing an allele-field string with any alias key, because lookup also tries
inherited species tables and alternate gene names. It is not a membership catalog.
CI regenerates the aliases, guards, identity catalog and audit, and checks every eligible source name and emitted
alias with `python scripts/validate_alias_sources.py`. Every eligible name must parse;
there is no allowlist of unparseable names.

`ipd_record_annotations.json` records all 419 abandoned IPD-MHC entries retained in
the pinned `IPD-MHC-3.17.0.0.xml` snapshot (across IPD-MHC release reports `0.1.0.0`
through `3.17.0.0`), with species/class/locus evidence from each cited live accession
record. The pinned 3.17.0.0 XML retains these entries and their
complete history. A matching accession with a different name fails for review. Missing
sequences alone never trigger exclusion. `current_records` counts source records
eligible after annotations (`source_records` minus `excluded_records`).

Excluded status applies to the active-source audit, not to name ownership or
parseability. The generator preserves every record's latest name in precedence
checks and includes documented historical aliases even for abandoned records.
`registry_allele_identities.json` additionally rolls each of the 419 abandoned
accessions and all its recorded names into a stable `IPD-MHC:<accession>` identity.
84 related public records are included so overlapping names expose their actual
candidates. Complete history in this explicit inventory may include partial-looking
old names; resolving those names still requires `use_allele_aliases=True` in `parse`,
and historical registry aliases never override curated keys or terminal targets
established in `allele_aliases.yaml` (e.g., curated `Mamu-A*11 -> Mamu-A1*011:01`,
`Mamu-A*08 -> Mamu-A1*008:01:01`, `Mamu-A*26 -> Mamu-A1*026:01`). The general
alias table's conservative partial-name rules remain unchanged.

No replacement accession is inferred. In particular `Paha-DP1*06:01` keeps its own
abandoned identity NHP10764 and is parsed without establishing an ontology gene or
asserting a DPB1 replacement. `Mafa-B*051:06:03` retains NHP11987 despite also
occurring in NHP04329's history (the same IPD tombstone pattern recurs across 50+
earlier abandoned records). Shared latest names in the pinned 3.17.0.0 XML include
`Mafa-DQA1*01:16:01` (public NHP04701 and abandoned NHP11988), `DLA-DRB1*097:01`
(public DLA04910 and public DLA07966), and `DLA-DRB1*09701` (abandoned DLA08202 and
abandoned DLA08399); name-only lookup retains every candidate. Two SLA
historical spellings (`SLA-DMA*0104` and `SLA-6*0102`) appear in both a public and an
abandoned record's history under distinct canonical names; `get_registry_identities`
exposes both candidates while `parse(..., use_allele_aliases=True)` preserves the
documented public redirect. Unresolved equivalence questions for `NHP11987`/`NHP11988`
are documented beside the annotations and tracked in #250. See
[Registry identities](docs/registry-identities.md) for runtime API contracts and
coverage.

The public maintainer API lives in `scripts/combine_allele_aliases.py`:
`RegistryRecord` and `AliasCandidate` hold source identities/provenance;
`read_ipd_xml`, `read_hla_history`, `read_hla_deletions`, and `read_curated_aliases`
read the documented source formats; `resolve_aliases` returns aliases, provenance,
and audit decisions. `protected_current_names` builds the sparse guards.
`read_ipd_xml` preserves every XML record, including abandoned stubs;
`partition_ipd_records(records)` returns eligible records and provenance-bearing
exclusions using the bundled source annotations. Apply it before auditing eligible
records. Use the full source records for name precedence and historical alias
candidates. `registry_identity_rows(excluded, records=())` returns deterministic JSON-ready
identity rows from those exclusions and their source-backed metadata, retaining
complete history. Missing metadata raises `KeyError`; duplicate accessions raise
`ValueError`. Pass all source records when an exclusion cites related records;
missing/mismatched related records or unannotated name collisions raise `ValueError`.
No replacement is inferred.
`write_aliases` and `write_current_name_guards` write deterministic YAML.
`alias_key`, `strip_species`, and `meaningful_alias` implement the documented
name-key and candidate policies. These helpers operate on paths, records and plain
mappings, independently of runtime parsing. Malformed required source structure
and cycles raise `ValueError`; file and decoding errors propagate. See docstrings
and `tests/test_alias_generation.py` for input/output contracts and source fixtures.

The separate `allele-classification` download group pins HLA 3.42.0 for the
single-field naming classifier. Its historical complete names remain recognized
when later releases add fields; this does not claim they are current registry
entries. Alias generation uses the current HLA 3.66.0 source exclusively.

Default padding widths are explicit compatibility settings in
`first_allele_field_widths.yaml`. They no longer depend on historical alias
frequencies, so refreshing this opt-in data cannot change default parsing.

## Regenerating serotype relationships

```bash
mhcgnomes data download --group serotype-hierarchy
python scripts/generate_serotype_hierarchy.py
```

The generator verifies the pinned IPD-IMGT/HLA 3.66.0 WMDA input hash and writes
`mhcgnomes/data/serotype_splits.yaml`. Only the split-antigen column defines the
broad/split graph; associated antigens are not allele assignments. CI regenerates
this graph and checks for drift. The curated `serotypes.yaml` remains the direct
assignment table; runtime expansion and its limits are documented in
[the nomenclature guide](docs/nomenclature.md#broad-and-split-serotype-candidates).
