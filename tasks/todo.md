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
  broken prefix inheritance. Suppressing inheritance now requires a group
  entry, so an ordinary species hands its prefix down like any other parent.
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
- **`prefix_provenance` is curated where it matters.** 467 entries derive
  "generated", 29 derive "group label", 11 are curated "designated" with a
  source read in this session, and 165 stay `None`. `None` is deliberately not
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

## Review round 2 (code review found a real bug in the same PR)

- **The 4+4 branch was missing the binomial guard.** The concatenated form was
  guarded on `len(scientific_parts) == 2`, the 4+4 form was not, so
  `Strix occidentalis caurina` claimed `StriOcci` and
  `Sapajus apella macrocephalus` claimed `SapaApel` -- both derived from their
  *parent* binomial -- while the safer concatenated form was withheld. The two
  other trinomials escaped only because their 4+4 collides with the parent, so
  the guard was accidental. This directly contradicted a README paragraph added
  by the same commit. Fixed, and pinned by a test naming both species.
- **Reverted mid-PR: classifying decorated labels as "group label".** An
  attempt to take `MusSp`, `Cosp`, `Trsp` and `Mana` off #131's list matched
  them with string patterns (`taxon[:2] + "sp"`, `taxon[:4]`), which is a guess
  about nomenclature, and it was wired into prefix inheritance as well.
  Measured against main it stripped the inherited `old prefix` from 18 species
  -- 16 `Mus`, plus `Coregonus clupeaformis` and `Tropheus moorii` -- an
  unmeasured behaviour change. Reverted: those four stay `None` and stay on
  #131's list, which is the honest answer.
- **The 4+4 collision census counted entries that cannot claim a form.** It was
  built over every latin name including trinomials, so `Canis lupus baileyi`
  vetoed `CaniLupu` for `Canis lupus` and `Balaenoptera musculus brevicauda`
  vetoed `BalaMusc` -- both now resolve to their binomial. Every subspecies
  added would otherwise have removed its parent's shorthand for free.
- **"generated" now means the emitter would emit it**, not merely that a
  generator function can produce the string. `LaniColl` on *Lanius collurio* is
  a curator tie-break never auto-generated for anyone, and used to claim
  "generated"; it reports `None`.
- **Nine of the eleven "designated" claims shipped without a URL**, against an
  explicit rule in CLAUDE.md and AGENTS.md. All eleven now cite one, and
  `test_every_designated_prefix_cites_a_source` fails if a future one does not
  -- verified by mutation.
- **Two tests could not fail.** `test_prefix_provenance_values_are_valid`
  asserted membership in a set that both producers are constrained to by
  construction; it is replaced by `test_designated_is_never_inferred`, which
  checks the invariant that actually matters. The `assert len(unknown) < 300`
  canary tested the wrong direction -- it passes a bulk assignment and fires on
  ordinary growth -- and is replaced by pinning the eight unknowns by name.
- **Unknown keys in species.yaml are now rejected.** A `prefix_source` typo
  used to load silently, leaving the YAML asserting a provenance the runtime
  never read.
- Also fixed from review: a docstring pointing at a nonexistent `group_node`, a
  stale numbered comment describing the deleted 5+5 tier and the wrong emission
  order, a `docs/curation.md` collision-table row still naming `ChryPict`, two
  species.yaml comments citing "5+5" above 4+4 prefixes, generated aliases
  duplicating the entry's own prefix, a duplicated trinomial test, a
  single-element `for` loop, and a "467" that is 466.
- **Not fixed, filed instead:** #134 (colliding 4+4 forms still resolve
  confidently to one side -- `ChryPict` gives a turtle to a caller who meant a
  pheasant; the README now says so, but whether to demote them to
  `context only prefixes` is a behaviour decision) and #135 (`_is_group_entry`
  hardcodes the string `"NHP"`; the fact belongs in the data).
- **Known and accepted:** this is a breaking parse change. 596 generated 5+5
  aliases and 10 curated ones stop resolving, and three species normalize to a
  new prefix. #128 laid out the choice between removing in one minor bump and a
  deprecation cycle, and the first was chosen. Recorded in the README tier
  section rather than a changelog, since the repo has no changelog.
- **Measured after the round-3 fixes:** 3 entries change `old_mhc_prefix`
  against main, all three the intended renames, down from 21.
- Bumped 3.41.0 to 3.42.0.
