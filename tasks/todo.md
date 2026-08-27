# Species inference for ambiguous and degenerate inputs

Tracking issues: #102, #103, #105

## Specification

- [x] Stop a bare species prefix from resolving to an arbitrary descendant
      species. A prefix is inherited by every descendant, so `BoLA` matches
      `Bos sp.` and also `Bubalus bubalis`; resolve it with the ladder
      `Species.get` already implements rather than letting the result sort
      order decide.
- [x] Rank ambiguous unprefixed gene symbols by whether a species declares the
      gene in its own ontology entry, not by how many genes it can see. A gene
      defined on a broad parent group is visible to every species beneath it.
- [x] Handle the case-normalized gene-name collision (`Ia1` vs `IA1`) so the
      species spelling the gene the caller's way wins.
- [x] Reject punctuation-only strings and the `n/a` family instead of falling
      through to the default species.
- [x] Keep explicit descendant prefixes, bare haplotype shorthand, and the
      existing bare-gene answers for model organisms working.
- [x] Measure the change against the bundled allele corpora rather than
      assuming a tie-break is inert.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- **#103** is fixed in `Parser.parse_multiple_candidates` at the point the
  species prefix is matched, by deferring to `Species.get`, which already
  resolves exact latin name, then exact prefix owner, then non-descendant.
  An earlier attempt added a species-depth term to the global `sort_key`
  instead; that worked but made one ambiguity's tie-break a rule governing
  every result comparison in the library, and raw tree depth is not
  comparable across clades. Fixing it where the ambiguity is created is
  narrower and leaves `result_sorting.py` untouched.
- Eight prefixes were affected, not just BoLA: `RT1 class I` was
  *Rattus villosissimus*, `NHP class I` was *Saimiri sciureus*.
- **#105** is fixed with `Species.declares_gene()`, collected inside the
  loader's existing validated gene walk so it cannot drift from `gene_names`.
  A first attempt ranked by the *size* of a species' own gene block, which
  fixed `BLB2` only by coincidence and regressed `DAB1`, `DBB1` and `Ia1`.
  Declaring the specific gene is the property that actually matters.
- Verified across all 315 ambiguous digit-containing gene symbols: there is
  now no case where the winner fails to declare the gene while some candidate
  does.
- **#102** turned out wider than reported: 254 punctuation-only strings
  returned *Homo sapiens*, and 14 of 69 common null markers returned a
  confident result. Both are zero now. Bare haplotype shorthand (`b/d`, `d`,
  `n`) is deliberately preserved.
- Blast radius: 1 of 11,558 names in the bundled netMHCpan/netMHCIIpan/IEDB
  corpora changes (`B12 class I`, crab-eating macaque to genus-level
  *Macaca sp.*). 206 bare gene symbols reachable through the API change, all
  from an inheriting species to a declaring one.
- Cold parse throughput unchanged (~0.067 ms/name). Results are now stable
  across `PYTHONHASHSEED` values.
- Filed #109 (water buffalo is parented under `Bos sp.`, a different genus)
  and #110 (`Pren class I` silently picks a winner for a colliding prefix).
  Left #104 open: its premise is wrong, `Mamu-I` and `H2-i` are real entities.
- Bumped 3.33.6 to 3.34.0. Minor rather than patch because bare gene symbols
  and class-only strings change species for downstream callers.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,209 tests; 91% statement coverage).
