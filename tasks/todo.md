# Put the four macaques under their genus node

Tracking issue: #123

## Review

- **Four of the five, not five.** #123 listed five primates sitting outside a
  genus node that exists. Four are macaques and move under `Macaca sp.` The
  fifth does not, and checking why was the useful part.
- **`Callithrix pygmaea` is not a Callithrix.** NCBI Taxonomy accepts
  *Cebuella pygmaea* (taxid 9493, lineage `... Callitrichinae > Cebuella`) and
  lists *Callithrix pygmaea* only as a homotypic synonym -- which is also where
  the entry's `old prefix: Cepy` comes from. Moving it under `Callithrix sp.`
  would have been a taxonomic error dressed up as a consistency fix. The entry
  keeps its parent, with the reason recorded on it, and the tree-shape test
  keeps it in the allowlist with the citation rather than as an open gap.
- **What the macaques gained.** 24-34 genes each, up to the 68 the genus node
  provides, so the names in the issue now parse:

  ```
  Mafu-A*01:01     None  ->  Macaca fuscata A*01:01
  Maas-DRB1*01:01  None  ->  Macaca assamensis DRB1*01:01
  ```

- **Two existing tests encoded the old inconsistency**, which is what
  `AGENTS.md` warns to check before assuming a failing test means the change is
  wrong:
  - `Maar-A` normalized to `A1`, because *M. arctoides* declared `A1` but not
    `A`. Every other macaque leaves `A` alone -- `Mamu-A`, `Mafa-A`, `Mane-A`
    -- so the old answer was the odd one out, not the new one.
  - An adversarial stickiness test used `Maar-A2` as a name that must not
    parse. It parses now, but to *M. arctoides* itself rather than by switching
    species, so it no longer exercises stickiness at all. Replaced with
    `Maar-BLB2` and `Maar-UAA`, which do.
- **One of my new tests was wrong too.** It asserted the reparented species
  have the same gene count as *Macaca mulatta*, which declares its own `K` on
  top of the genus list and so has one more. Changed to assert every gene the
  genus declares is visible to them.
- **Measured:** 0 of 11,558 corpus names change. Four entries change
  `old_mhc_prefix` (`Maar`/`Maas`/`Mafu`/`Malo` -> `RhLA`), which is the
  umbrella every other macaque already carries.
- Bumped 3.44.0 to 3.45.0: names that returned `None` now parse, and `Maar-A`
  normalizes differently.
