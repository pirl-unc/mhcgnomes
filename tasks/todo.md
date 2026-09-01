# Curate prefix provenance from the IPD-MHC species tables

Tracking issue: #131 (partial -- 113 entries still unestablished)

## Review

- **50 entries marked `designated`, each citing an IPD-MHC group species
  table.** The count goes 11 -> 61, and the unestablished tail 163 -> 113.
  Rather than 163 individual lookups, the group tables list every species and
  its designation in one page each, so this is eight fetches:

  | group | rows | marked |
  |---|---|---|
  | DLA | 10 | 9 |
  | CeLA | 33 | 29 |
  | SLA | 3 | 3 |
  | BoLA | 4 | 3 |
  | OLA | 2 | 2 |
  | RT1 | 2 | 2 |
  | CLA | 1 | 1 |
  | ELA | 1 | 1 |

  Each was read verbatim rather than from a summary, per `AGENTS.md`, and every
  row was checked against our prefix before marking.

- **Zero of the 56 species IPD lists in these groups is missing from our
  ontology**, and the prefixes agree everywhere except five.

- **Four of the five disagreements are known or newly filed:**
  - `Canis aureus`: IPD designates `Caau`, which is in published use for the
    goldfish *Carassius auratus*. Our entry keeps `CaniAure` and holds `Caau`
    as a context-only prefix -- #112's resolution, working as intended.
  - `Hyperoodon ampullatus`: IPD designates `Hyam`, which resolves to the Rio
    Grande silvery minnow. Same shape, same resolution.
  - `Delphinapterus leucas`, `Neophocaena asiaeorientalis`, `Orcinus orca`: our
    canonical prefix is a generated 4+4 (`DeleLuca`, `NeopAsia`, `OrciOrca`)
    while IPD designates `Dele`, `Neas`, `Oror` -- and those already resolve to
    the right species as aliases, with nothing else claiming them. So we emit a
    name we invented in preference to the published one. Filed as **#146**,
    since swapping them changes normalized output for three species.

- **The remaining 113 are the harder half**, and the eight pinned in
  `test_unestablished_provenance_stays_none` show why: `OmLA`, `FLA`, `GoLA`,
  `MaLA`, `RhLA`, `RLA`, `ChLA`, `OrLA` are group-level `_LA` codes, and
  IPD-MHC publishes no group page for any of them -- `/group/FLA/` is a 404.
  Establishing those means the primate nomenclature reports rather than a
  species table.

- **A new test pins the citations themselves.** Every IPD group named in a
  `species.yaml` URL must be one of the eleven IPD publishes, read off
  `https://www.ebi.ac.uk/ipd/mhc/`. Its first draft failed on `FISH` and
  `CHICKEN`, which are real groups I had left out of the set -- so it caught my
  error rather than a data error. Verified by mutation: mistyping `CeLA` as
  `CELA` in a citation fails it.

- **Measured:** 0 of 11,558 corpus names change. Provenance only.
- Bumped to 3.45.1.
