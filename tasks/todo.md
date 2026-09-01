# Prefer IPD's designation over a prefix we generated

Tracking issue: #146 (found while curating #131, stacked on that branch)

## Review

- **Three cetaceans emitted an invented name in preference to a published
  one.** *Delphinapterus leucas*, *Neophocaena asiaeorientalis* and *Orcinus
  orca* carried generated 4+4 prefixes while the IPD-MHC CeLA table designates
  `Dele`, `Neas` and `Oror` -- codes that already resolved to exactly those
  species as aliases. So `parse("Oror-DQB1")` normalized to `OrciOrca-DQB1`.
- **Nothing forced it.** Each of the three codes is derivable by the 2+2 rule
  from its species and no other, nothing else claims any of them, and none is
  a context-only prefix anywhere. `git log -S` traces them to a bulk "Add 12
  missing species" commit that applied the 4+4 default without checking IPD --
  unlike `Caau` and `Hyam`, where the short code genuinely belongs to another
  species in published use and the 4+4 is the right answer (#112).
- **Both spellings still parse**; the generated form stays an alias. Only the
  canonical prefix and therefore normalized output change.
- **Measured:** 0 of 11,558 corpus names change -- no bundled corpus name uses
  any of the six spellings.
- Bumped to 3.46.0: normalized output changes for three species.

