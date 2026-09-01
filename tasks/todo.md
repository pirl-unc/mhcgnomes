# Let a species be named by more than three words (#177)

## Review

- **Found by a measurement, not by a report.** #176 required that every printed
  form parse back. 148 did not, all CD1 -- and chasing why turned up something
  much wider than CD1.

- **The species matcher tried three leading tokens, then two, then one.**
  Forty-one common names in the ontology are longer than that once hyphens are
  counted: "north atlantic right whale", "thirteen-lined ground squirrel",
  "kemp's ridley sea turtle", "rio grande silvery minnow". **None of them could
  be parsed at all.** Not a CD1 problem -- a whole class of input that silently
  failed.

- **My first diagnosis on #177 was wrong, and testing it is what corrected it.**
  I filed the issue blaming hyphens and apostrophes in common names. It is the
  word count: `gray bellied night monkey-CD1a`, with no punctuation at all,
  failed identically.

- **The window is now a named bound with a test.** `MAX_SPECIES_NAME_TOKENS = 5`
  covers the longest name curated, and the test fails if a longer one is added
  -- otherwise that name silently stops parsing, which is the state all 41 were
  in.

- **Measured:** 28 of 36,752 corpus names change, **every one of them `None` ->
  a result**. Nothing stops parsing; the loop already tried longest-first, so a
  wider window cannot change a shorter match. All 41 long common names now
  work. 16,521 tests pass; setting the bound back to 3 fails 16 of them.

- **#177 keeps the residual, with a sharper diagnosis.** Round-trip failures
  drop 148 -> 130. The rest are common names whose *first* token contains a
  hyphen -- "long-haired rat-CD1a" tokenizes as `[long-haired, rat-cd1a]`, so
  no leading-token query can match. That is a tokenizer question, not a window
  one.
- Bumped to 3.61.0.
