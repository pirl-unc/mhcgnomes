# Sweep the four group nodes, the last entries never checked (#131)

## Review

- **A gap in my own method, not in the sources.** The GenBank sweep in #169
  skipped every `<Genus> sp.` row -- `if species.endswith(" sp."): continue` --
  because a group node has no organism to search under. So four of #131's
  fifteen had never actually been searched, while I was describing the list as
  exhaustively checked.

- **Searching under the genus instead finds nothing**, in nuccore or protein:

      Coregonus + Cosp   0        Manacus + Mana   0
      Tropheus  + Trsp   0        Mus     + MusSp  0 as a prefix

- **`MusSp` returns 18 records and none of them count.** They are *Mus spretus*
  microsatellites named `MUSSP-16`, `MUSSP-17`, `MUSSP-18` -- a coincidental
  string, the same false-positive shape as `Xetr` appearing only as clone tags
  for bitter taste receptors.

- **They stay `None`, and now for a checked reason rather than an unchecked
  one.** Reclassifying them as "group label" would need the predicate that also
  gates prefix inheritance, and 18 species inherit these as `old_mhc_prefix`.
  That trade is recorded on #131 and has not changed.

- **All fifteen of #131's remaining entries have now been searched**, which was
  not true before this.

- No data changed, so no corpus measurement applies. 16,994 tests pass.
- Bumped to 3.63.2.
