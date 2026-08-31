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
- [x] Reparent `Homo sapiens` under `Primata sp.` without letting it inherit
      `NHP`, and cite the source next to the entry.
- [x] Measure: A/B every name in the bundled corpora, and diff every field of
      all 671 species objects, between `main` and the branch.
- [x] Sweep every parent link for the same class of defect and file what turns
      up rather than folding it in.
- [x] Correct the README, `docs/curation.md` and `AGENTS.md`, which had
      generalized one exception into a model.
- [x] Pin the invariants in tests.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.

## Review

- **The fix is one parent link and one `old prefix`.** The issue proposed
  either renaming the node or inserting an extra level above it. Neither was
  needed: `create_species_for_latin_name` already hands a parent's prefix down
  only when the child does not declare an `old prefix` of its own, so spelling
  out `old prefix: HLA` opts human out of the `NHP` umbrella while leaving it
  in the taxon. The parent link and the umbrella prefix were never the same
  mechanism.
- **Authority.** https://www.ebi.ac.uk/ipd/mhc/group/NHP/ -- "a specialist
  database for the Major Histocompatibility Complex genes of Non-Human
  Primates ... Apes and both Old World and New World monkeys". The prefix is
  exclusionary by definition, which is why the opt-out has to be explicit and
  is now tested.
- **Measured inert.** 0 of 11,558 corpus names change. Diffing 15 structural
  fields across all 671 species objects between `main` and the branch shows
  exactly one difference: `Homo sapiens.parent`. Human's gene count is
  unchanged at 56 because it already declares all sixteen genes `Primata sp.`
  owns -- a test now pins that, so a future primate-wide gene cannot land in
  `HLA` by inheritance unnoticed.
- **The docs were over-corrected and are now fixed.** #120 read the water
  buffalo edge as proof that the tree is "prefix scope, not phylogeny". A sweep
  of every parent link shows exactly one edge in the ontology crosses a genus
  boundary -- the buffalo -- and `Homo sapiens` was outside `Primata sp.` only
  because nothing had opted it out. The buffalo exception stands; the
  generalization does not.
- **Filed rather than folded: #123.** The same sweep found five primates
  (`Macaca arctoides`, `M. assamensis`, `M. fuscata`, `M. leonina`,
  `Callithrix pygmaea`) sitting outside their own genus node, so they inherit
  almost no genes and `Mafu-A*01:01` does not parse while `Mamu-A*01:01` does.
  Reparenting them is also 0/11,558, but it hands each one 49 macaque genes by
  inheritance, which is a scientific claim that wants reading rather than
  measuring. A test pins the list of five so it cannot grow silently.
- Bumped 3.39.0 to 3.40.0 -- minor rather than patch, because
  `compatible_with` now answers `True` for human against `Primata sp.`
