# A shared identifier names the containing node (#129)

## Review

- **Found by asking what else the round-trip technique would find.** Sweeping
  "does every identifier a species advertises resolve back to it" turned up 109
  exceptions. 105 were umbrella prefixes resolving to their owner, which is
  correct and by design. **Four were not.**

- **`Species.get` disagreed with `parse` about the same string.**
  `Species.get("swordtail")` returned None while
  `parse("swordtail class I")` answered *Xiphophorus sp.* The public lookup and
  the parser giving different answers is the bug; which one is right is
  secondary.

- **Another comment describing behaviour the code did not implement.** The
  ladder's step 3 says "prefer the species that isn't a subspecies (no parent
  with same identifier)" and tested `sp.parent_species is None` -- "no parent at
  all" -- so it only ever fired for root entries. Umbrella prefixes were
  unaffected because step 2 catches them: `MusSp` is *Mus sp.*'s own prefix. A
  shared *common name* has no step 2, so it fell through to None. Same shape as
  #160, where the case-aware ranking key had never fired.

- **The predicate is now named and tested directly.** `_containing_species`
  returns the one claimant that contains all the others, or None.

- **The ontology has zero aliases with unrelated claimants**, because #112 and
  #134 moved every contested string -- Caau, Hyam, Moal, Orla -- to `context
  only prefixes`. So the "decline to guess" branch is unexercised by data,
  which is exactly why it is now tested with a constructed pair instead of
  borrowed ones. My first draft asserted Caau was still ambiguous; it is not,
  and the test failed and said so.

- **Measured:** 0 of 36,752 corpus names change -- the parser already resolved
  these; only the public lookup was wrong. 16,994 tests pass; restoring the old
  predicate fails 4.
- Bumped to 3.63.0.
