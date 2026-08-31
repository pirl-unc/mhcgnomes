# Prefix provenance, and retiring the 5+5 tier

Tracking issues: #128, and #129 apart from its point 3

Four changes, in increasing order of reach.

## Specification

- [x] Rename `_is_taxonomic_prefix` to `_prefix_is_derived_from_name`, which is
      what it computes. Pure rename.
- [x] Stop the tautonym false positive: only group entries hand a prefix down,
      so `Bubo bubo` (prefix `BuboBubo`) is no longer treated as an umbrella.
- [x] Remove the 5+5 tier: the generator, its collision index, and the ten
      curated `other prefixes` entries that were 5+5 forms.
- [x] Make the concatenated binomial the default generated alias.
- [x] Rename only the contested 4+4 prefixes, retiring the off-book tie-breaks.
- [x] Add `Species.prefix_provenance`, curated for "designated" and derived for
      the rest.
- [x] Measure against a worktree of `main`; update README and `docs/curation.md`.

## Review

- **`_prefix_is_derived_from_name` says what it does.** The old name claimed a
  taxonomic judgement it never made: it is a string test, and `NHP` passes it
  while being a paraphyletic database section. The docstring now says so.
- **The tautonym bug was latent, and is fixed.** Six species whose curated
  prefix equals their own concatenated binomial -- `Naja naja` -> `NajaNaja`,
  plus `Grus grus`, `Asio otus`, `Bubo bubo`, `Tyto alba`, `Bufo bufo` -- were
  classified as umbrella nodes. All six are leaves, so nothing inherited
  wrongly today, but adding a subspecies to any of them would have silently
  broken prefix inheritance. Inheritance now requires a group entry.
- **5+5 is gone.** `_make_5_5_prefix` and `_GENERATED_5_5_PREFIX_COUNTS` are
  deleted, along with ten curated aliases (`ChrysPicta`, `GaviaGange`, ...) all
  added by 49e536e, the commit that introduced the scheme. Evidence it was
  safe: its own docstring called it backward compatibility, `docs/curation.md`
  never listed it, no name in the 11,558-name bundled corpora used one, and no
  species token in the sibling `mhcseqs` dataset (590 distinct, 19,290 rows)
  used one either.
- **Three contested prefixes renamed, off-book forms retired.** `ChryPict` is
  derivable from both a painted turtle and a golden pheasant; the pheasant
  keeps the literature-style `Chpi` and the turtle takes `ChrysemysPicta`.
  `LaniCola` (a hand-tweaked 4+4) and `LeucisLeucis` (a 6+6) belonged to no
  documented form and became `LaniusCollaris` and `LeuciscusLeuciscus`. All
  three old spellings stay parseable as `other prefixes`.
- **`prefix_provenance` is curated where it matters.** 469 entries derive
  "generated", 29 derive "group label", 11 are curated "designated" with a
  source read in this session, and 163 stay `None`. `None` is deliberately not
  "designated": a prefix we did not generate is not proven to be in published
  use, which is the `Caau` lesson. The remaining sweep is #131.
- **Measured against a worktree of `main`:** 0 of 11,558 corpus names change,
  despite three species changing their canonical prefix -- no corpus name uses
  a generated form.
- **Deliberately not done: #129's point 3.** That issue proposes emitting the
  concatenated binomial for every species without an attested prefix, which
  would rename 467 of 672 entries and change `to_string()` for each. Asked, and
  the answer was to rename only the contested prefixes for now. #129 stays open
  for the wider change; `prefix_provenance` is the field it would key off.
- Bumped 3.41.0 to 3.42.0.
