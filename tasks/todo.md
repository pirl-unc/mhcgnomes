# Document that the species tree is prefix scope, not phylogeny

Tracking issues: #109, #115 (both closed as not-a-bug)

## Specification

- [x] Establish whether `Bubalus bubalis` under `Bos sp.` is wrong, from the
      published water buffalo literature rather than from taxonomy.
- [x] Record the answer where the misreading happens: README, curation guide,
      and AGENTS.md.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- **No data change.** The placement is correct and my own #109 proposal would
  have broken real parses. Two of us filed the same bug independently -- #109
  from here, #115 downstream -- so the gap was documentation, not curation.
- The tree is a **prefix-scope hierarchy**: a `parent` says "this species may
  be named under the ancestor's umbrella prefix". `Homo sapiens` attaching to
  the root rather than under `Primata sp.` is the clearest evidence, since
  human alleles are never written `NHP-*`.
- The literature confirms it for water buffalo: `Bubu-DRB` is orthologous to
  `BoLA-DRB3` and buffalo sequences are assigned to cattle loci by
  trans-species polymorphism (PMC3313522; PMID 12580780). IPD-MHC files the
  species in the BoLA group.
- The link is load-bearing. `Bubalus bubalis` declares only `DQA`, `DQA1` and
  `DQB`; `Bubu-DRA`, `Bubu-DRB3`, `Bubu-DQA2` and `Bubu-DQB1` all parse by
  inheritance, and `Bubu-DRB` normalizes to `Bubu-DRB3` -- exactly the
  orthology the papers describe -- only because of it. Detaching drops the
  species from 55 visible genes to 11. I had measured that drop while
  proposing the change and read it as an acceptable cost; it was the evidence
  against the change.
- Residual, not addressed: buffalo also inherits the BoLA class I loci, and
  no water buffalo class I sequences are published. That is permissive parsing
  of names nobody writes rather than a wrong claim, and tightening it means
  per-locus evidence review across every group node.
- AGENTS.md gains the inverse of the lesson added last time: do not assume our
  curation is wrong either, and check what depends on a structure before
  changing it.
- Bumped 3.38.0 to 3.38.1. Docs only; no behaviour change.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,489 tests; 91% statement coverage).
