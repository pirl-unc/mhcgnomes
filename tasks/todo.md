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

- [ ] #191: implement, review, test, PR, merge, publish, verify.
- [ ] #200: implement, review, test, PR, merge, publish, verify.
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
review findings. PR/CI/merge/publication pending.
