# Source correctness and predictable public interfaces

Previous release: PR #240 merged and shipped as 3.66.1; clean PyPI installation
passed all 3,734 alias checks. This plan replaces its completed checklist.

## Contract and sequence

1. **Registry aliases (#241, #238, #197).** Read the actual IPD-MHC XML schema
   and current IMGT/HLA history/deletions. Pin authoritative releases and
   checksums. Gather current identities before collecting historical mappings.
   Current names take precedence over stale historical or curated redirects;
   report conflicting mappings rather than picking one. Respect field
   boundaries and accession identity; preserve the evidence-backed Mamu aliases.
   Reject cycles. Emit deterministic counts and a decision audit so regeneration
   cannot silently skip a source. Test real-shaped source fixtures and audit all
   current source names and all emitted aliases before shipping.
2. **Missing input (#218).** Validate before caches/tokenization. None and
   scalar missing numeric values follow raise_on_error (None or ParseError).
   Other non-string inputs raise a clear TypeError. Apply the same policy to
   parse, Parser.parse, parse_gene_class and infer_mhc_class, without blanket
   exception swallowing or coercing arbitrary objects to allele strings.
3. **DataFrames (#219).** Add documented parse-option forwarding and
   raise_on_error. Preserve legacy record columns and order, add input/outcome
   information, support Haplotype, and return one row per input in tolerant mode.
   Share a public outcome-to-row API with the CLI; keep formatting separate.
4. **CLI parity (#220).** Expose species, aliases, explicit-species policy,
   required result types and MHC class. Validate incompatible arguments and
   unknown result types before processing. Keep table/TSV/JSON and strict exit
   semantics consistent with the Python API.
5. **Public helpers (user correction / #225).** Inventory directly tested
   package helpers and promote them to public names with clear scope,
   parameters, results, errors, and documented API location. Tests exercise
   those public contracts. New directly tested helpers follow the same rule.

Keep is_allele_group boolean, expression graded, and bare Mamu-B17 a locus.
Document that group=False does not establish registry membership, a complete
sequence or normal expression. Preserve the deprecated cytosolic spelling.

Each coherent PR bumps the version, runs ./format.sh, ./lint.sh and ./test.sh,
passes CI, merges into verified main, and runs ./deploy.sh from clean main.
Use existing artifacts for the #83 manual-upload fallback. Verify each release
from PyPI outside the checkout. Keep the shared virtualenv outside this work.

## Checklist

- [x] Review current code, issues, lessons and user correction.
- [x] Source spec and authoritative evidence; regression fixtures.
- [x] Source readers, conflict policy, audit output and regenerated data.
- [x] Audit current names, aliases, default-parser differences and source coverage.
- [x] Ship registry-source PR and verify PyPI.
- [x] Implement and verify missing-input policy.
- [x] Implement and verify DataFrame outcome API.
- [x] Implement and verify CLI option parity.
- [x] Promote directly tested helpers and document their contracts.
- [ ] Ship interface/helper changes with fresh-PyPI verification.
- [ ] Recheck relevant downstream issues and record remaining work.

## Review

Source review: all 59,180 current source records checked; 59,179 parse identically
with aliases off/on, and the existing NHP10764/Paha-DP1 failure is explicitly
tracked in #243. All 5,805 emitted alias keys reach their targets (5,796 named-gene
targets also reparse identically; 9 geneless Saha targets preserve source class).
All 17,750 baseline inputs retain their default result type and normalized text.
Source history does not increase the resolution of partial names. The historical
one-field classifier retains its prior pin. Added guards for inherited and
alternate-gene aliases (#242), decoupled padding from alias counts (#244), and
recognized the source-defined BoLA SV suffix (#235). Documentation builds strictly.
Format/lint/full suite passed (17,309 tests; 2 skipped). CI and PyPI verification
will be recorded after shipping. Guard lookup uses canonical species identity,
independent of the configurable display prefix.


## Interface implementation contract

Validate scalar input before caches; strings pass unchanged, pandas scalar missing
values join None/NaN, and other types raise TypeError even in tolerant mode.
DataFrame tolerance catches ParseError only, retaining input order and one row per
input. A public outcome-row function supplies normalized text, status and error;
legacy to_record columns (especially full gene names) remain available. The CLI
projects that shared row into its existing display columns, with a short gene
name. Empty frames have fixed outcome columns. Haplotype records may be absent,
but normalized results still have rows. Unknown parse options propagate normally.
CLI options forward the public parser constraints; invalid result types and
mutually exclusive species options fail before parsing. The public-helper audit
includes direct calls, imports and monkeypatch references; promote those helpers
and document their module/class scope without broadening their algorithms.


Source PR #245 merged as e4c041c and deployed as 3.66.2. All CI checks passed
(Python 3.9–3.12 and exhaustive regeneration/audit). ./deploy.sh confirmed PyPI;
#83 required upload of the existing artifacts. A clean PyPI environment verified
source regressions, 5,796 named-gene alias reparses, retained classifier behavior,
and pip check. The release checkout is clean.

Interface review: direct-helper AST audit finds no private function references
from tests (including imports and monkeypatch strings), and all existing test
function names are preserved. New APIs are documented in docs/helper-api.md;
strict docs build and all 71 interactive documentation examples pass. All 17,750
baseline default result types/texts remain unchanged. Format/lint/full suite
passed (17,364 passed, 2 skipped). CI and PyPI verification remain.
