# Put Homo sapiens back in the primate order

Tracking issue: #122

`Primata sp.` carries the prefix `NHP`, which IPD-MHC defines as "Non-Human
Primates". `Homo sapiens` was therefore attached straight to the root, so the
library answered `False` to "is a human a primate?" -- a node named for a taxon
that includes humans, scoped to a prefix that excludes them.

## Specification

- [x] Establish from the authority what `NHP` means and whether IPD files
      humans in that group.
- [x] Check whether the parent link and the umbrella prefix are actually the
      same mechanism, or two separable ones.
- [x] Reparent `Homo sapiens` under `Primata sp.` without letting `NHP` name
      it by any route, and cite the source next to the entry.
- [x] Check every consumer of the parent link, not just prefix inheritance.
- [x] Measure: A/B every name in the bundled corpora, and diff every field of
      all 671 species objects, between `main` and the branch.
- [x] Sweep every parent link for the same class of defect and file what turns
      up rather than folding it in.
- [x] Correct the README, `docs/curation.md` and `AGENTS.md`, which had
      generalized one exception into a model.
- [x] Pin the invariants in tests.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.

## Review

- **The fix is a parent link plus a first-class exclusion.** The issue proposed
  either renaming the node or inserting a level above it. Neither was needed,
  but the first attempt -- opting human out of the umbrella by spelling out
  `old prefix: HLA` -- was not enough either. Code review found it only blocked
  one of four consumers of the parent link:

  ```
  parse("NHP-E*01:01", species="Homo sapiens")  ->  HLA-E*01:01
  ```

  So the exclusion is now declared on the node that owns the prefix, and there
  is a runtime query for it:

  ```yaml
  Primata sp.:
    prefix: NHP
    prefix excludes:
      - Homo sapiens
  ```

  `Species.can_name(other)` is ancestry minus anything an ancestor excludes.
  `compatible_with` follows it, and so does the ancestor-to-descendant
  conversion in `function_api`. `is_ancestor_of` and `is_descendant_of` stay
  purely taxonomic, which is what the issue was actually asking for.
- **Authority.** https://www.ebi.ac.uk/ipd/mhc/group/NHP/ -- "a specialist
  database for the Major Histocompatibility Complex genes of Non-Human
  Primates ... Apes and both Old World and New World monkeys". The placement
  itself cites NCBI Taxonomy: Homo sapiens (9606) sits in Primates (9443).
- **Measured against a worktree of `main`, not a stash.** 0 of 11,558 corpus
  names change; `compatible_with` is identical across all 450,241 species
  pairs; 15 structural fields across all 671 species objects differ in exactly
  one place, `Homo sapiens.parent`. The first round of this measurement used
  `git stash`, which only reverts uncommitted work and so compared the branch
  against itself -- recorded in `tasks/lessons.md`.
- **The inertness guard now covers every inheritance channel.** Gene names were
  only one of them: gene properties, gene families, class II locus groupings
  and seven side tables keyed by ancestor latin name all flow down too. A
  pseudogene flag added to `Primata sp.` reaches `HLA` and passed the original
  name-only check; it now fails.
- **The docs were over-corrected and are now fixed.** #120 read the water
  buffalo edge as proof that the tree is "prefix scope, not phylogeny". Exactly
  one parent link points at another genus's node -- the buffalo -- and `Homo
  sapiens` was outside `Primata sp.` only because nothing expressed the NHP
  exclusion. The buffalo exception stands; the generalization does not.
- **Filed rather than folded: #123.** The same sweep found five primates
  (`Macaca arctoides`, `M. assamensis`, `M. fuscata`, `M. leonina`,
  `Callithrix pygmaea`) sitting outside their own genus node, so they inherit
  almost no genes and `Mafu-A*01:01` does not parse while `Mamu-A*01:01` does.
  Reparenting them is also 0/11,558, but it hands each one 49 macaque genes by
  inheritance, which is a scientific claim that wants reading rather than
  measuring. A test pins the list of five so it cannot grow silently.
- Bumped 3.39.0 to 3.40.0 -- minor rather than patch, because `Species.can_name`
  is new public API.
