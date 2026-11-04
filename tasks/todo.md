# Accession identities and historical-name parsing (#248)

## Scope and evidence

Cover all 76 accessions in IPD-MHC 3.7.0.0's Abandoned list that remain in the
pinned 3.8.0.0 XML. Primary source: https://www.ebi.ac.uk/ipd/mhc/version/v3700/.
The live IPD API was checked for every accession on 2026-11-04; all remain
abandoned and their names/history match the pinned XML. Two names overlap other
accessions (#250), one in history and one as a latest name; there are no documented
successor links in those records. Preserve separate accession identities; do not
merge records by similar spelling or invent replacement alleles.

## Implementation contract

- Expand sourced annotations to all 76 records, recording accession, status,
  species/class metadata and primary-source citations.
- Generate a small runtime identity catalog from those annotations and the pinned
  XML's complete nomenclature history. Use namespaced IPD-MHC accession IDs as
  stable keys. Keep abandoned status separate from whether a name parses.
- Provide a public immutable registry-identity API resolving accession IDs,
  namespaced IDs, latest recorded names and historical names. Expose all candidates
  for duplicate latest names rather than selecting an
  arbitrary record. Include the two related public accessions to represent these
  collisions faithfully. Latest recorded names take precedence over history.
- Parse accession IDs without requiring the alias flag. Keep historical
  canonicalization opt-in with use_allele_aliases as confirmed by the user. Explicit
  registry lookup always resolves history.
- Expose the shared identity on parsed results. Default parsing of partial/group
  names must not silently claim a specific full accession. Mutations or resolution
  loss must not retain an unsupported identity.
- Reuse Allele for supported loci. Represent the abandoned DP1 designation with
  AlleleWithoutGene and the source's class II metadata, preserving its own ID;
  do not add an unsupported biological locus or equate it with DPB1.
- Route registry matches through the existing species/class/result-type policies;
  support Python, DataFrames and CLI consistently and preserve raw input.
- Regenerate and audit aliases/guards and the new identity catalog. Test every
  accession and recorded spelling, identity equality, status, independent IDs,
  partial names, mutations, filters, strict species and interface serialization.
- Bump the minor version, run format/lint/full tests and docs checks, land by PR
  and deploy from clean main; verify installation from public PyPI.

## Checklist

- [x] Read instructions/lessons and inspect parser/model interfaces.
- [x] Fetch and compare all 76 official API records with pinned XML/history.
- [x] Create feature branch and write implementation contract.
- [x] Resolve alias-policy preference and document public contracts.
- [x] Implement sourced annotations and deterministic identity generation.
- [x] Implement runtime identity lookup and parser integration.
- [x] Verify all identities/spellings and filters across interfaces.
- [x] Review generated/default-behavior changes and run required checks.
- [ ] PR, CI, merge, deployment and clean-install verification.
- [x] Record local verification results and prioritize the next dependency block.

## Review

Implemented 76 abandoned identities plus two related public records. All 102
recorded spellings of the abandoned inventory parse, and raw/namespaced accession
IDs select their records without aliases. The one duplicate latest name exposes
both candidate accessions and no singular identity/status. All 363 focused checks
pass. Default parsing compared with installed 3.68.1 changes only the previously
unparseable Paha-DP1*06:01 designation. Source audit passes 59,104 eligible records,
5,805 historical aliases, and all 78 indexed identities. Strict docs build and both
new executable documentation examples pass. Required format/lint/full-suite gates
pass: 17,712 tests passed and 2 skipped. PR, CI and deployment remain pending.

The source annotations remain an explicit inventory, not a complete active-record
catalog. #248 remains open for reconciliation beyond the 3.7 abandonment list;
#250 tracks the two unresolved cross-accession relationships.

## Collision-driven revision

The full current-and-history overlap audit found NHP11987/NHP04329 and
NHP11988/NHP04701. Add the two cited public records as related identities. Public
plural lookup returns all candidates; singular lookup returns None if ambiguous.
A name-only Allele may have multiple candidate IDs; an accession input selects its
record only when the parsed name still matches. Do not use raw input to retain
identity after truncation or mutation. Keep structural Allele equality unchanged;
registry record equality/deduplication uses the stable identifier.

Next dependency block after this release: continue sourced lifecycle reconciliation
under #248 and resolve the evidence questions in #250 before merging accessions.
Downstream, openvax/mhctools#631 can adopt mhcgnomes nomenclature/identity APIs; its
CLI argument handling (#643) is independent. Public-helper cleanup (#225) and stale
documentation (#223) can follow without changing scientific identity claims.
