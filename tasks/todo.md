# Remove two species.yaml keys nothing ever read

Tracking issue: #139

## Review

- **I filed #139 with a wrong claim, and checking it settled the design.** The
  issue said neither `MhcPatr` nor the transposed `MhcPtar` resolves. Only the
  second is true: `Species.get("MhcPatr")` is `None`, but `parse` strips a
  leading `Mhc` as a fallback, so `parse("MhcPatr-A*01:01")` gives
  `Patr-A*01:01`. The `alias: MhcPtar` key was therefore carrying nothing --
  a typo of a string that already works without it -- so there was no
  behaviour to preserve and no reason to implement the key.
- **`haplotype prefix: Hp` had nothing behind it either.** `haplotypes.yaml`
  has no `Sus scrofa` entry, and none of `Hp-1.1`, `SLA-1.1`, `Hp1.1` or
  `Susc-Hp-1.1` parses, so wiring the key into `Species` would have given a
  prefix with no haplotypes under it. The fact that swine haplotypes carry an
  `Hp` prefix is kept as a comment on the entry, and curating the haplotypes
  themselves is #143 -- the prerequisite for any field.
- **The hygiene rule that would have caught this.** `SPECIES_ENTRY_KEYS` exists
  so a misspelled key cannot load silently while the YAML asserts something the
  runtime never read. Whitelisting a key nothing reads does the same thing with
  more confidence behind it, which is exactly what happened when I added the
  frozenset in #132 and listed both of these to keep the file loading.
  `tests/test_ontology_hygiene.py` now asserts every accepted key is fetched in
  `species.py`, and that the data uses no key the loader rejects.
- **The test caught its own first draft.** It looked for
  `species_info.get("<key>")` and flagged `genes`, `gene properties` and
  `gene families`, which are fetched with a default argument. Broadened, then
  verified by mutation: adding a bogus key to the frozenset fails it.
- **Measured:** 0 of 11,558 corpus names change.
- Bumped to 3.44.1 -- data and hygiene only, no behaviour change.
