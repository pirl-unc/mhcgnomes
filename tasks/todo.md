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

---

# Check our prefixes against the IPD-MHC namespace in CI

Tracking issue: #112 (stacked on #146)

## Review

- **#112 asked for the namespace, and I now have it.** The issue proposed a
  curated reservation set so the prefix generator could not claim a code IPD
  has assigned elsewhere. Its own follow-up comment established the generator
  is not the culprit -- it never mints 2+2 codes -- but the underlying gap
  stands: nothing in this repo knows what IPD has designated, which is why
  `Caau` and `Hyam` were found by a manual sweep months late.
- **`mhcgnomes/data/ipd_designations.yaml`** transcribes 55 designations across
  8 groups, verbatim from the species tables. Non-runtime curation data, like
  `underrepresented_taxa_source_registry.yaml`; nothing loads it at import.
- **The check allows exactly two outcomes per row**: our prefix is the IPD
  code, or the code is context-only on our entry because another species holds
  it in published use. Today that is 53 and 2. A third case cannot be added to
  the allowlist without a canary test failing.
- **My first version of the test missed the failure the issue is named for.**
  It returned early when an IPD code resolved to nothing, so a mutation that
  made the goldfish claim `Cala` passed -- two owners make `Species.get`
  ambiguous, and the designation silently stops working, which is the same
  defect wearing a different face. Now asserted, and all three mutations fail:
  a squatted code, a dropped designation, and a removed species.
- **Measured:** 0 of 11,558 corpus names change. Test-time only.
- Bumped to 3.46.1.

