# Registry accession identities

An accession identifies a registry record even when its designation changes or the
record is abandoned. mhcgnomes 3.69 adds an explicit identity index for the **76
IPD-MHC records abandoned in release 3.7.0.0**, retained in the pinned 3.8.0.0 XML.
Two related public accessions are included to represent overlapping names.
This is a curated inventory, not complete coverage of IPD-MHC, IMGT/HLA, or GenBank.

```python
from mhcgnomes import get_registry_identity, parse

identity = get_registry_identity("Mamu-AG*01")
assert identity.identifier == "IPD-MHC:NHP00355"
assert identity.canonical_name == "Mamu-AG*01:01"
assert identity.aliases == ("Mamu-AG*01",)
assert identity.status == "abandoned"

by_id = parse("NHP00355")
by_namespaced_id = parse("IPD-MHC:NHP00355")
by_latest_name = parse("Mamu-AG*01:01")
by_history = parse("Mamu-AG*01", use_allele_aliases=True)
assert by_id == by_namespaced_id == by_latest_name == by_history
assert by_id.registry_id == "IPD-MHC:NHP00355"
```

Accessions and latest recorded names work without the alias flag. Historical
canonicalization remains opt-in in `parse`: `parse("Mamu-AG*01")` keeps the partial
name and has no registry identity. The explicit `get_registry_identity` lookup
includes history by default; set `include_aliases=False` to exclude it.

A namespaced ID is the stable key for joins and deduplication. Names are labels;
`canonical_name` means the source's latest recorded designation, including when
abandoned. It does not establish a currently valid allele, complete molecule,
sequence identity with another accession, or normal expression. `is_allele_group`
remains a naming classifier. Registry status and expression annotations answer
separate questions.

## Lookup contract

- `get_registry_identity(value, include_aliases=True)` accepts a string accession,
  namespaced accession, or full species-prefixed recorded name. It ignores case
  and surrounding whitespace, preserving stars and colon boundaries. Unknown
  or ambiguous strings return `None`; non-strings raise `TypeError`. It performs no network call.
- `get_registry_identities(value, include_aliases=True)` uses the same matching
  rules and returns a tuple of candidates sorted by identifier, or `()` if unknown.
  Accessions outrank names, and latest recorded names outrank historical names.
  Duplicate latest names retain both candidates.
- `registry_identities()` returns a cached read-only mapping from namespaced IDs
  to immutable `RegistryIdentity` values. Invalid or duplicate bundled data raises
  `ValueError`; file and JSON errors propagate.
- `RegistryIdentity` exposes `registry`, `accession`, `identifier`, `canonical_name`,
  `aliases`, `names`, `status`, `species_name`, `mhc_class`, `locus`, `source_release`,
  `status_source`, and `record_source`. Aliases are an immutable tuple. Equality and
  hashing use only the namespaced identifier. `to_record()` returns a new dictionary
  containing the six `registry_*` fields described below.
- `mhcgnomes.registry_identity.build_registry_index(identities, include_aliases=True)`
  builds a read-only lookup index from an iterable of `RegistryIdentity` values.
  Values are identifier-sorted tuples of candidates using the precedence above,
  independent of input order. Duplicate identifiers raise `ValueError`. This
  helper does not infer equivalence or discard equal-priority candidates.

Parsed results expose `registry_identity` and `registry_id`. They are `None` outside
this inventory, for ambiguous names, and for partial, mutated, or aggregate results.
`registry_identities` and `registry_id_candidates` expose the candidate records and
IDs as tuples. An unambiguous original accession or historical name selects its
record only while the complete parsed name still matches it. Reducing allele
resolution drops an identity when the resulting name no longer matches a complete
record. Display-prefix preferences do not change the identity. Source spellings,
including IPD's leading `W`, are retained in the normalized names.

Registry matches go through the normal species, class and result-type filters.
An accession explicitly identifies its source species: `require_explicit_species`
accepts it, `default_species` does not override it, and a conflicting strict
`species=` is rejected. Unknown accession IDs fail parsing under the usual
`raise_on_error` policy; they are never fetched or guessed.

Most records return `Allele`. `NHP10764` / `Paha-DP1*06:01` returns
`AlleleWithoutGene` with the source's class II designation, because DP1 is not an
established gene in the ontology. It retains its own accession and abandoned
status; no DPB1 replacement or new biological locus is asserted.

## DataFrames and CLI

`to_record()` and DataFrame rows for known identities include `registry_id`,
`registry_accession`, `registry_name`, `registry_status`, `registry_aliases`, and
`registry_source`. A shared-name result instead includes `registry_id_candidates`,
without asserting a single status. Unindexed results omit these optional fields. CLI output keeps
its existing columns and includes the same metadata in `properties`.

```bash
mhcgnomes --format json NHP00355 IPD-MHC:NHP10764
mhcgnomes --format tsv --use-allele-aliases 'Mamu-AG*01'
```

The public building block `Parser.parse_registry_allele(name)` returns an `Allele`,
`AlleleWithoutGene`, or `None` for unknown/ambiguous input using this Parser's alias setting. It uses exact
recorded spellings and source metadata, without padding heuristics. Non-strings
raise `TypeError`; inconsistent species metadata raises `ValueError`. It does not
apply species/class/type filters, pairing or truncation: use `parse` for those.

## Sources and collisions

The [IPD-MHC 3.7.0.0 report](https://www.ebi.ac.uk/ipd/mhc/version/v3700/) supplies
abandoned status. The pinned XML supplies complete nomenclature history. All 76
live accession records were checked on 2026-11-04 and agreed on names, history and
abandoned status. Citations live beside each annotation in
`mhcgnomes/data/ipd_record_annotations.json`; generation produces
`registry_allele_identities.json`, and CI verifies regeneration and every spelling.

One designation also occurs in a different accession's history:
`Mafa-B*051:06:03` is retained on abandoned `NHP11987`, and is a previous name of
public `NHP04329` (`Mafa-B*051:26`). Latest recorded names retain precedence over
historical redirects, so it resolves to `NHP11987`. The source does not explicitly
state accession equivalence; the records are not merged. Evidence and follow-up
are recorded in [#250](https://github.com/pirl-unc/mhcgnomes/issues/250).

A second designation is the latest name on **two** records:
`Mafa-DQA1*01:16:01` belongs to public `NHP04701` and abandoned `NHP11988`.
Name-only parsing returns an `Allele` with both `registry_id_candidates` and
`registry_id=None`; it cannot determine which record was intended. Both accession
IDs parse definitively. The documented historical `Mafa-DQA1*01:16` resolves to
`NHP04701` with aliases enabled. This collision is also tracked in #250.

```python
shared = parse("Mafa-DQA1*01:16:01")
assert shared.registry_id is None
assert shared.registry_id_candidates == ("IPD-MHC:NHP04701", "IPD-MHC:NHP11988")
assert parse("NHP11988").registry_id == "IPD-MHC:NHP11988"
assert parse("NHP04701").registry_id == "IPD-MHC:NHP04701"
```

`Allele` equality still compares structured nomenclature. The two accession parses
above therefore have equal allele names but different registry identities. Use
`registry_id` for record joins and preserve it in storage: converting an accession
parse back to a shared name loses the information that selected one record.
