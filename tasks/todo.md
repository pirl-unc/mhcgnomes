# Reviewed bug-fix PR series

## Scope and order

User-approved order: #191 -> #200 -> #196 -> #199 -> #202/#205. Also retain the
preceding request for #189 and release bugs #185/#204; handle those afterward.
Hold #201 for scientific review. One focused PR per item below, with its own
version bump, code/source review, required checks, CI, merge, deployment from
clean main, and public-PyPI smoke check. Do not stack an unreviewed PR or stop at
merge. Never infer allele validity from a group flag or infer biological identity
from a coincident name. Keep historical aliases opt-in and accession IDs direct.

## PR contracts

1. **#191 non-MHC gene names.** Verify Uty/Kdm6c and Klra22 in primary gene
   authorities. Extend the existing whole-token non-MHC guard/classifier so these
   complete names cannot be split into H2-K alleles. Preserve reported non-MHC
   symbols without inventing cross-gene alias equivalence. Cover bare, prefixed,
   species-constrained, case and punctuation forms through public APIs; preserve
   actual H2-K alleles and declared ontology helper genes.
2. **#200 trailing class qualifiers.** Trace every normalization/tokenization path
   that discards the qualifier. Reject a compound allele-plus-class statement as
   a single MHC entity consistently for class I/II and species-qualified forms.
   Preserve standalone class names and legitimate descriptive allele syntax.
   Check Python, Parser, classifier, DataFrame and CLI paths and raw input.
3. **#196 serotype hierarchy.** Read the official broad/split relationship source,
   pin source/version/hash if generation consumes it, and represent transitive
   memberships without replacing a reported broad type by a specific allele.
   Audit the whole hierarchy, not just B12; retain direct versus inferred
   membership distinctions, deterministic output and cycle/conflict checks.
4. **#199 chicken aliases.** Verify the two reported BF2 identities through the
   paper's GenBank accessions and IPD records. Make compact and re-punctuated old
   names resolve consistently with aliases enabled; do not solve the renaming by
   zero-padding or expand curation to unsupported alleles.
5. **#202/#205 species identity.** Verify domestic dog, wolf and DLA nomenclature
   scopes from taxonomy and IPD. Preserve domestic-dog specificity and exact
   aliases while keeping DLA parsing/inheritance compatible. Make decorated
   scientific-name fallback case/underscore independent without fuzzy matches or
   bypassing ambiguity rules. Enumerate affected ancestry/prefix consumers.
6. **#189 paper extraction.** Reject generic hyphenated terms, avoid nested partial
   duplicates, preserve source identifiers, deduplicate exact within-paper rows,
   and make docx collection consistent. Measure against the committed corpus;
   keep ontology and generated research artifacts out of this mechanical PR.
7. **#185/#204 release tooling.** Isolate DEPLOY_PYTHON in tests and verify an
   interpreter can actually execute the build entry point before artifacts are
   removed. Exercise importable-but-unrunnable packages and documented overrides
   with local fixtures; do not trigger a real release from tests.

## Review and verification for each PR

- Inspect the complete final diff, source citations, public helper contracts and
  effects on adjacent parse paths. Tests calling helpers directly use public APIs.
- Run ./format.sh, ./lint.sh, ./test.sh; add focused regression tests that first
  demonstrate the reported behavior. Run applicable source generation/audits and
  docs checks. Record counts/results and any limitations below.
- Verify PR base=main, reviewed head SHA and all required CI before merging.
- Run ./deploy.sh (no arguments) from clean merged main. If #83's invalid-publisher
  failure recurs, upload the already-built artifacts; do not re-run deploy.
- Install the exact version from public PyPI in a repository-local release
  environment or /tmp, verify behavior and pip check. Leave shared-virtual-env alone.

## Progress

- [x] #191: implement, review, test, PR, merge, publish, verify.
- [x] #200: implement, review, test, PR, merge, publish, verify.
- [ ] #196: source review, implement, review, test, PR, merge, publish, verify.
- [ ] #199: source review, implement, review, test, PR, merge, publish, verify.
- [ ] #202/#205: source review, implement, review, test, PR, merge, publish, verify.
- [ ] #189: implement, corpus comparison, review, test, PR, merge, publish, verify.
- [ ] #185/#204: implement, review, test, PR, merge, publish, verify.

## Results

Prior stream: PR #251 shipped as 3.69.0, verified all 76 abandoned records and two
related public accessions. The repository's previous plan was captured before
release; PR #251 now records successful merge, publication and clean-install checks.

### #191 review (3.69.1)

Added exact KDM6C and KLRA22 entries to the existing whole-token classification
table, with UniProt P79457 and MGI:2136939 citations. Both remain their reported
symbols; no Klra22 -> Klra1 equivalence is asserted. Reviewed strict/default species,
prefix, case and punctuation paths, ontology ownership and genuine H2-K parses.
Regression check before change: 22 failures; after change: 54 focused tests pass.
Required format/lint/full suite pass: 17,734 passed, 2 skipped. No outstanding
review findings. PR #252 merged as d1601a9 after all CI checks passed. Published
3.69.1; workflow 42083774309 reproduced #83, so the validated wheel/sdist were
uploaded with Twine. Clean PyPI install passed API/CLI/registry smoke and pip check.

### #200 implementation contract

The class-token helper gains an explicit, documented switch for accepting allele
and pair results. Only suffix syntax disables them; class descriptions before the
name retain their meaning. Class restriction of named haplotypes and serotypes,
standalone class names, and gene descriptions remain supported. Test class I/II,
alias mode, direct Parser APIs, strict/tolerant functions, DataFrame/CLI errors,
and the helper itself. Do not reinterpret the compound as a fully typed molecule.

### #200 review (3.69.2)

Reviewed final diff: the suffix call alone disables Allele/AlleleWithoutGene/Pair
results in the existing class-token helper. Leading descriptions, standalone
classes, genes and named haplotype restrictions retain their paths. API/classifier,
DataFrame/CLI tests cover class I/II, groups, pairs, gene-less alias targets,
case/token variants and both alias modes. Additional explicit-species and
singleton-collapse checks pass. Required format/lint/full suite pass: 17,817
passed, 2 skipped; 83 focused tests pass. Original regressions failed before the
runtime change. No outstanding findings in this fix. Pre-existing serotype class
metadata gap filed separately as #254; no scientific behavior was inferred for it.
PR #255 merged as 84546c5 after all CI checks passed. Published 3.69.2;
workflow 42086386324 reproduced #83 and the exact validated artifacts were
uploaded using Twine. Fresh PyPI API/DataFrame/CLI and registry smoke checks
and pip check pass.


### #196 implementation spec

Source: https://hla.alleles.org/pages/wmda/wmda/ explicitly defines rel_ser_ser.txt
columns: locus;antigen;split antigens;associated antigens. Only column 3 is the
broad/split relation. Column 4 is associated antigen designations, NOT alleles.
Official current broad/split table confirms B12 -> B44/B45.
Pinned release 3.66.0 at b2055ea33ef464781b9e8ecab20b275b6704f878:
https://raw.githubusercontent.com/ANHIG/IMGTHLA/b2055ea33ef464781b9e8ecab20b275b6704f878/wmda/rel_ser_ser.txt
sha256 4c821ce7fc6900dc4c6d9be6cb6dd343224c66f7e8d4a9a405a23c1c9040bde4
Local file: /tmp/mhcgnomes-rel-ser-ser-3.66.0.txt
23 broads, 57 edges; runtime tables have 21 broads / 53 edges. Six cellular
specificities Dw6/Dw7/Dw11/Dw17/Dw18/Dw19 have no allele assignments here. Preserve
all 57 source relationships in the generated graph but do not invent candidates
or add unsupported allele mappings. State this scope explicitly in docs/tests.

Proposed minimal architecture (not yet implemented; reevaluate as needed):
- Add pinned source to external_sources.json under group serotype-hierarchy,
  default false; manifest test count 8 -> 9. Use verified .external-data source.
- Public generator functions parse source strictly, reject bad rows, duplicates,
  self/cycles/multiple parents, source-inconsistent prefixes. Emit deterministic
  mhcgnomes/data/serotype_splits.yaml with cited source/version/hash comments.
- Public runtime helper expands direct memberships through descendants. Validate
  graph even disconnected nodes; leave direct map untouched, deduplicate/sort
  expanded candidate lists. Runtime no network. Only return existing direct names
  (all 21 supported broads already exist); missing cellular nodes remain in graph.
- Keep serotypes.yaml and serotypes_generated.yaml as curated direct assignments,
  unchanged. data.direct_serotypes loads old map; data.serotypes expanded map.
  Expose Species.direct_serotypes as immutable normalized direct assignments,
  alongside Species.serotypes as effective candidate lists. Add optional final
  constructor argument for backward compatibility, pass from species loader with
  same inheritance/identifier resolution. Species.copy resolves registry object
  by name (no need to serialize every new field).
- Existing Parser.get_serotype already reads Species.serotypes; original
  Serotype.name/raw_string stay B12, .alleles contains B44/B45 members. Reverse
  readers of Species.serotypes see consistent candidates. Direct assignments
  accessible separately. No need to add Serotype dataclass provenance fields.
- Runtime graph public API may be exposed as Species.serotype_splits if useful;
  avoid unnecessary API surfaces beyond clear documented helper and direct map.
- Tests: real B12 retains B*44:15 and includes B*44:02 + B45 members; all supported
  source edges have subset membership through parse and raw maps; reverse B*44:02
  returns B44 and B12; B15 relation excludes B70/B71/B72 (current tests claim
  otherwise). Synthetic multi-level/cycle/conflict/order/duplicate tests; no
  propagation between unrelated broads or from broad down to split; direct maps
  unchanged and immutable. Test parse modes, singleton collapse, alias mode,
  serialization, copied raw string and CLI/DataFrame original B12 label.
- Existing tests/test_serotype_who_definitions.py claims broad/split candidate
  disjointness scientifically; correct those claims, test direct assignments vs
  expanded candidates instead, use official graph rather than old invented B15
  relationships. Do not assert universal biological disjointness of direct data.
- Add external CI source download + generation + git diff checks. Required
  format/lint/full tests, generation verification, docs build, review/PR/CI/merge/
  deploy/public PyPI smoke. Consider version 3.70.0 for additive public direct map.
- Separate pre-existing class metadata defect is issue #254. Keep it explicitly
  pending unless fixing it becomes necessary for this narrowly scoped change.

### #196 review (3.70.0)

Implemented the pinned WMDA graph (23 broads, 57 edges), upward candidate
expansion and immutable Species.direct_serotypes. All 21 broads with curated
assignments expand; B12 grows from 1 to 24 candidates including B*44:02 and
B45 members. Six cellular labels remain graph-only without invented assignments.
Original B12/type and hierarchy regressions fail before runtime integration.
Reviewed source-column semantics, graph validation, every supported edge, reverse
membership, alias/singleton modes, copy/serialization, immutable direct mappings,
non-HLA preservation and CLI/DataFrame labels. Corrected the tests' unsupported
broad/split disjointness and B15/B70 claims against the primary source.
Required format/lint/full suite pass: 17,841 passed, no skips (installed the
repository's declared openpyxl test extra locally). Focused checks: 101 pass.
Pinned source regenerates byte-identically; tampered input fails before output
is touched; strict docs build passes. Pre-existing serotype metadata (#254) and
compact-member alias over-specification (#256) remain separately tracked.
No outstanding review findings in this change. PR/CI/merge/publication pending.
