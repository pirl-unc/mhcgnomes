# A contested prefix names nobody, and group-ness lives in the data

Tracking issues: #134, #135

## Specification

- [x] #135: replace the hardcoded `latin_name == "NHP"` in `_is_group_entry`
      with a `group: true` key, keeping the `" sp."` suffix as the shorthand.
- [x] #134: stop a 4+4 form derivable from two species resolving confidently to
      whichever of them curated it.
- [x] Give the two species that still held a contested form as their canonical
      prefix their concatenated binomial instead.
- [x] Measure against a worktree of `main`; update README and `docs/curation.md`.

## Review

- **#135 is a three-line change.** `_is_group_entry` reads `group: true` from
  the entry and falls back to the `" sp."` suffix, and `NHP` declares the flag.
  `SPECIES_ENTRY_KEYS` already rejects unknown keys, so the flag cannot be
  silently misspelled. Group-ness drives both prefix inheritance and
  `prefix_provenance`, so the next non-taxon section added -- IPD-MHC also
  groups by `FISH` and `CHICKEN` -- no longer has to be remembered in code.
- **#134: a contested form now resolves only under an explicit `species=`.**
  `ChryPict`, `LaniColl` and `LeucLeuc` are each derivable by the 4+4 rule from
  two species. The generator already refused to emit them, but that only
  suppressed the generated copy -- whichever claimant curated the form won
  silently, so a caller who meant a golden pheasant and wrote `ChryPict` got a
  painted turtle. Both claimants now list the form under
  `context only prefixes`, which is the mechanism the ontology already uses for
  `Moal` and `Orla`:

  ```
  parse("ChryPict-B")                                   -> None
  parse("ChryPict-B", species="Chrysolophus pictus")    -> Chrysolophus pictus
  ```

- **Two more canonical prefixes moved to the concatenated binomial.**
  *Lanius collurio* held `LaniColl` and *Leucogeranus leucogeranus* held
  `LeucLeuc`; both named their species only by curation order. They are now
  `LaniusCollurio` and `LeucogeranusLeucogeranus`, forms that were already
  parseable as generated aliases, so the rename promotes rather than invents.
- **The rule is written down**, since the next collision will want it: a prefix
  two entries can derive is curated by neither as a plain alias -- context only
  on both, concatenated binomial as each canonical prefix.
- **Measured against a worktree of `main` (3.42.0):** 0 of 11,558 corpus names
  change. 16 structural fields differ across the 6 species involved, and no
  others.
- Bumped 3.42.0 to 3.43.0 -- three forms stop resolving bare, and two species
  normalize to a new prefix.
