# Import the evidenced prefix aliases

Tracking issue: #136

## Review

- **Recounted first, because the issue's numbers were measured against 3.40.**
  Against 3.47.1 the mhcseqs registry has 339 evidenced pairs (up from 294),
  every one with an evidence URL. 118 already resolved, 23 were genuinely
  contested, and 7 of the apparent collisions were not collisions at all:
  `OmLA`, `MaLA`, `GoLA`, `RhLA`, `RLA`, `ChLA` and `RT1` resolve to the genus
  node that owns them while the evidenced row names a species beneath it. That
  is the umbrella working, and those are left alone.
- **`mhcgnomes/data/evidenced_prefix_aliases.yaml`** carries the import: 183
  species, 196 rows, each with its own `status` and `evidence` URL. Per
  `(species, alias)`, as point 3 of the issue's model asks -- one species can
  have current, historical and database spellings from different sources.
- **Global vs context-only is computed, not curated.** An alias claimed by one
  species and unclaimed elsewhere becomes a global alias; anything claimed by
  two or more, or already owned in `species.yaml`, becomes context-only. That
  is point 2 of the model, and computing it means the decision cannot go stale
  as species are added. 141 global, 32 context-only.
- **Three things the first cut got wrong, all caught by existing tests:**
  - **It overrode a deliberate holdback.** `Otel-DAB`, `Phtr-UA` and `Phco-UA`
    started parsing, and `tests/test_birds.py` asserts they must not.
    `underrepresented_taxa_source_registry.yaml` marks all three `blocked` /
    `registry_only` -- the holding area `docs/curation.md` describes for source
    signal not stable enough to parse with. An attested spelling does not
    outrank that, and the loader now reads the registry to enforce it.
  - **It made `B` a species prefix.** Real chicken nomenclature (B-F, B-L), but
    as a bare prefix it shadows the mouse haplotype `b` and `b/d` stopped
    parsing. Aliases shorter than three characters are not imported globally --
    the same reason the single-letter HLA fragments stay out of unprefixed
    resolution (#113).
  - **A refactor broke the claimant count** by keying on the alias instead of
    the species, which silently turned contested aliases global. `GPLA` and
    `XLA` stopped resolving, which is what surfaced it.
- **One of my new tests was wrong rather than the code.** It expected
  *Cyprinus carpio* to carry `Cyca` as context-only; the carp already owns
  `Cyca` as its prefix, and it is the three *other* claimants that get it
  context-only. The owner is never demoted by someone else's evidence.
- **Measured:** 0 of 11,558 corpus names change. Verified by mutation --
  ignoring the holdback fails 8 tests, allowing short aliases fails 3.
- **Not in scope:** 17 rows name species absent from the ontology, including
  *Spalax ehrenbergi* and its `Smh` system name (point 4 of the model). Adding
  taxa is a different job from importing aliases for taxa we have.
- Bumped 3.47.1 to 3.48.0: 141 strings that resolved to nothing now resolve.
