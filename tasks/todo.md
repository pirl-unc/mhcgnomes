# Alias identity audit and predictable resolution (#231, #232)

## Scope and acceptance criteria

Prioritize incorrect biological identity and process-dependent output over
packaging cleanup. Keep alias resolution opt-in and preserve default parsing.
Treat allele field boundaries as meaningful: modern `A*02:172` must not match
the legacy key `A*02172`. Try the canonical gene before alternate gene names,
with a deterministic order for alternates. Resolve documented renames to a
stable terminal spelling; prevent cycles rather than hanging or guessing.

Read primary IMGT/HLA history/deletion records before changing alias targets.
Keep provenance next to curated data. Check every alias source and target,
parser entry paths, composite results, and multiple Python hash seeds.

## Plan

- [x] Read repository instructions, lessons, recent implementation and open issues.
- [x] Select #231/#232 as the first foundational correctness work.
- [x] Reproduce failures; verify implicated identities against primary records.
- [x] Implement boundary-preserving, deterministic alias lookup and regressions.
- [x] Audit all bundled aliases and current registry names for unintended rewrites.
- [x] Review new group/expression APIs and triage #218–#228 with explicit decisions.
- [x] Bump patch version; run `./format.sh`, `./lint.sh`, `./test.sh`.
- [ ] Review diff, open PR against main, verify CI/base/head, merge.
- [ ] Run `./deploy.sh` on clean main, publish existing artifacts if required,
      and smoke-test a clean PyPI install.
- [x] Read relevant downstream issues and identify the next dependency block.

## Review

Verified: 17,294 tests passed, 2 skipped; formatting/lint and strict docs build
passed. All 3,734 gene-bearing alias keys resolve to equal result objects and
remain equal on reparse. Alias regeneration reproduces the shipped YAML.
Four hash seeds agree. Current HLA 3.66.0 audit found the two additional
source-data conflicts filed as #238; these are explicitly outside this engine
fix. No scientific curation changes were inferred from names alone. Python-floor changes, API exposure solely because
tests use helpers, and bulk deletion of research artifacts are not prerequisites
for alias correctness.

## Executive review and queue

- Keep `is_allele_group` boolean for compatibility, but treat it as a naming
  classifier. False is not proof of registry membership, a complete sequence,
  uniform expression, or a unique whole protein (G/P groups remain distinct).
  The pinned single-field table needs regular refresh alongside alias sources.
- Keep `cell_surface_expression` graded. `low` must remain distinct from
  `absent`; None means unreported, not normal. Keep the misspelling only as a
  deprecated compatibility alias.
- Keep bare `Mamu-B17` as its locus and require an explicit allele spelling for
  the legacy alias. Preserve opt-in aliases and the original raw string.
- First release: #231/#232 and discovered null-annotation bug #239. Default
  results were compared on 17,750 names drawn from the repository's text/CSV
  inventories and alias keys/targets, with identical inputs and separate
  baseline/working-tree imports: zero differences.
- Immediate next correctness block: #238 (current-name conflicts), #197
  (retirement coverage), and registry-source refresh. HLA history reuses
  A*30:100 across two accessions; a current spelling must not be blindly
  followed as a historical alias. HLA02908 had Q removed in August 2026.
- Then #218 -> #219 -> #220: define missing/invalid-input behavior first,
  carry parse options and row outcomes into DataFrames, then expose the same
  options in the CLI. Avoid blanket catches and preserve existing DataFrame
  columns during migration. #200 (swallowed qualifiers) is another correctness
  priority; #235 is a small independently sourced annotation fix.
- #221/#222/#223: consolidate configuration, remove shipped maintainer inputs,
  and separate historical plans from current docs. Retain scientific provenance
  and reproducible evaluation inputs; do not bulk-delete them merely for size.
  Release docs currently contradict the PR-only rule and describe broken
  trusted publishing as the only publishing path.
- #224: parameterize generated cases only after verifying identical input and
  assertion coverage. This is useful maintenance, below identity fixes.
- #225: reject blanket public exposure of helpers. Tests calling a private
  function do not establish a supported API contract. Expose only concrete
  downstream capabilities and document the rest where the logic lives.
- #226/#227/#228: separate Python support policy from dependency cleanup.
  Removing an unused direct NumPy dependency and adding newer-Python CI are
  reasonable. Do not require pandas 3 or drop working Python versions solely
  for stack uniformity; establish a compatibility need and version the policy.
  Leave frozen paper provenance separate from runtime dependencies.
- #237 CLI completion/latency follows correctness and CLI option parity.
- #83 remains an external PyPI trusted-publisher configuration problem. Use the
  documented manual upload of already-built artifacts if deployment exits 3.
- An upstream IPD-MHC correction report is warranted once the 33 discrepant
  rows are packaged with accession-level primary evidence. Do not send a
  blanket off-by-one allegation based only on the previous session's summary.

Downstream dependency order after the alias foundation: mhcseqs #92/#95/#96/#97
(parse once, keep identity and annotations, remove duplicate prefix inference
and broad exception swallowing), then mhctools #631 (canonical display plus
explicit ambiguity policy). Those changes need build/output comparisons;
cosmetic spelling alone must not turn a serotype into one allele.
