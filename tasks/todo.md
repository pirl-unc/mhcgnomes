# An opt-in policy for printing only attested prefixes (#129)

## Review

- **The issue proposes this, and I had not read it closely enough.** #129's
  "API/compatibility shape" section says the change "could ship as an explicit
  formatting policy first, then become the default in a documented minor
  release". The 467-species migration was declined; the opt-in policy had never
  been on the table. I had been reporting the whole issue as blocked on a
  decision that only covered half of it.

- **It reads a curated judgement rather than making a new one.**
  `Species.prefix_provenance` is what #131 spent its length populating:
  "designated" means a URL or PMID sits beside the entry. So the policy is one
  branch -- designated keeps its short prefix, everything else prints the
  concatenated binomial.

- **One property, not ten signatures.** Every `to_string` in the package reads
  `species_prefix`, so the policy lives there. No call-site churn, and
  `MhcClass`, `Haplotype`, `Serotype` and a bare `Species` all inherit it.

- **Two recursions, both caught immediately.** `Species.prefix` delegates to
  `species_prefix`, so reading `.prefix` inside the policy recursed until the
  stack gave out; the same for `unambiguous_prefix_for`'s fallback. Both now
  read `canonical_mhc_prefix`, the underlying curated field.

- **Thread-local, not a module global**, so a policy set by one caller cannot
  change what another thread is midway through formatting. There is a test.

- **Found a pre-existing bug while measuring.** Requiring that every printed
  form parse back showed **148** corpus names that do not -- all CD1, where
  `Gene.to_string` renders class `Id` genes with the *common species name*:
  "gray-bellied night monkey-CD1a". Identical count on main, so this change
  neither caused nor worsened it. Filed separately.

- **Measured:** 0 of 36,752 corpus names change under the default policy. Under
  ATTESTED, 25,389 printed forms differ and every one parses back. 16,473 tests
  pass.
- Bumped to 3.60.0.
