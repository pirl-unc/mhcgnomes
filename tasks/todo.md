# Re-spell three prefixes to the form the emitter produces (#129, #131)

## Review

- **Asked, and got an answer.** These three had been sitting in #131's
  "unestablished" list and #129's "you declined the rename" bucket at once,
  which is not a place a decision can be made from. The call was to re-spell
  them to 4+4, keeping the old spellings as aliases.

- **What was wrong with them.** Each followed no rule this library implements:

      EudyChrys   4+5, a shape no tier has produced since 3.42.0 removed 5+5,
                  while its own siblings are EudyFilh and EudyScla
      MesoCriAu   not 2+2 (Meau), not 4+4 (MesoAura), not the binomial, next
                  to a hamster spelled CricGris
      NeosScha    not even a truncation of the genus -- Neomonachus gives
                  "Neom", not "Neos"

  None was attested in the registry, the literature or IPD.

- **All three new forms were already aliases**, so promoting them collided with
  nothing: `Species.get("EudyChry")` resolved to the right penguin before this.

- **`EudyChry` carries a note.** It is also what the 4+4 rule would give
  *Eudyptes chrysolophus*, the macaroni penguin, which this ontology does not
  carry -- which may well be why the odd 4+5 form was chosen. A test fails if
  that species is ever added, so the tie has to be broken deliberately.

- **#131 drops 19 -> 16.** Not by finding a source but by removing a false
  question: a prefix the emitter would produce is one we minted, and now says
  so instead of reporting `None` and looking like an unchecked claim about the
  outside world.

- **Measured:** 113 of 36,752 corpus names change, every one of them one of the
  three renames and nothing else. Old spellings still parse and normalize to
  the new form. 16,423 tests pass.
- Bumped to 3.58.0.
