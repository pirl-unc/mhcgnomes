# Curate prefix provenance from the IPD-MHC NHP table

Tracking issue: #131 (48 entries still unestablished)

## Review

- **64 more entries marked `designated`.** The count goes 128 designated and
  48 unknown, from 61/112 before. Between this and the earlier batch, every
  IPD-MHC group species table with a published page has now been transcribed
  and checked.
- **The NHP table was the one I had skipped**, because it is large enough that
  a fetch summary cannot be trusted for it -- and it proved the point: the
  fetch reported "Total: 68 rows" while listing 66. So I did not rely on it
  alone.
- **Every row was confirmed against two independent sources.** The IPD fetch,
  and the `ipd_current` rows of the sibling mhcseqs registry, which was curated
  separately from the same authority. Only rows where both agree *and* our
  prefix already matches were marked:

  ```
  confirmed by both, prefix matches ours : 64
  in the IPD fetch only                  :  0
  conflicts                              :  0
  absent from our ontology               :  0
  ```

  Zero conflicts across 66 rows is itself worth recording: our primate prefixes
  agree with IPD everywhere.
- **What is left is a different kind of problem.** 48 entries: 12 group nodes
  and 36 short codes. The eight pinned in the canary test are `_LA`-style group
  codes -- `OmLA`, `FLA`, `GoLA`, `MaLA`, `RhLA`, `RLA`, `ChLA`, `OrLA` -- and
  IPD publishes no group page for any of them, so establishing those means
  reading the nomenclature reports rather than a species table.
- **Measured:** 0 of 11,558 corpus names change. Provenance metadata only.
- Bumped to 3.48.1.
