# Annotate abandoned IPD accession NHP10764 (#243)

## Spec

IPD-MHC's 3.7.0.0 (2021-07) release report explicitly lists accession NHP10764,
Paha-DP1*06:01, under Abandoned:
https://www.ebi.ac.uk/ipd/mhc/version/v3700/
The pinned 3.8.0.0 XML retains a sequence-less stub. Treat its documented status
as source metadata; do not infer a replacement, add DP1 to the ontology, or
create an alias to the separately accessioned DPB1 name.

Add a small source-annotation JSON file scoped to the pinned XML filename,
accession and exact name. Store status, release/date, source URL and the absence
of an established replacement. A public, documented maintainer helper partitions
IPD source records into eligible records and excluded records with provenance.
Reject mismatched identities so annotation drift cannot silently hide a record.
Both alias generation and the runtime source audit use that helper. The generated
audit retains the excluded record and total coverage; current-name guards omit it.
Remove the unexplained unparseable-name allowance: every eligible name must parse.
This is an explicit annotation inventory, not a complete registry-status catalog.

## Checklist

- [x] Read instructions/lessons, confirm primary source and current main.
- [x] Create feature branch and review this implementation contract.
- [x] Implement annotation, shared source partition and generated audit.
- [x] Test identity scope, unknown stubs, no inferred alias, and audit strictness.
- [x] Regenerate artifacts; check expected-only changes and all source records.
- [ ] Update docs/lessons; bump 3.68.1; run format, lint, full tests.
- [ ] Open PR against main, verify CI, merge, deploy and check clean PyPI install.
- [ ] Review relevant follow-up issues and record final evidence in the PR.

## Review

Source audit: 59,179 eligible records parse with aliases off/on; all 5,805 aliases
pass. The generated alias table is byte-for-byte unchanged; only the abandoned
name is removed from current-name guards. All 19 source-generation tests, format,
lint and the strict docs build pass. The full suite is in progress. Broader retained
abandoned-stub reconciliation is filed as #248. A new regression initially assumed
Paha-DPB1*06:01 was supported; corrected it to verify the actual requirement (no
inferred alias) through the public alias lookup instead. Previous interface PR #246 shipped as
3.67.0; its clean-install verification and follow-up triage are recorded in that PR.
