# Species inference for ambiguous and degenerate inputs

Tracking issues: #102, #103, #105, #106, #107, #110, #112

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
- [x] Reclassify Patr-AL from `Ia` to `Ib`, with the primary literature cited
      in the ontology next to the gene.
- [x] Remove the duplicate `old prefix: Pren`, and give the two Klein-code
      collisions to the species IPD-MHC designates.
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
- **#107** asked whether Patr-AL is really `Ia`. It is not. The paper that
  described the locus is titled "A Novel, Nonclassical MHC Class I Molecule
  Specific to the Common Chimpanzee" (Adams, Cooper & Parham, J Immunol
  2001;167:3858, PMID 11564803): three allotypes differing at two residues,
  present on ~50% of chimpanzee MHC haplotypes, expressed at low level, and
  diverged from classical MHC-A >20 Mya. Gleimer et al. (J Immunol
  2011;186:1575, PMID 21301043) restate it as non-classical and group it with
  HLA-E/F/G. Moved to `Ib`, which is where the ontology already puts that
  family. hitlist and IEDB were right.
- **#106** is a duplicate of #103 describing the same eight prefixes; fixed by
  the same change.
- **#110** turned out to be a data fix, not a parser one. `Pren` is
  *Presbytis entellus*, the former name of *Semnopithecus entellus*;
  *Theropithecus gelada* also carried it as an `old prefix`, which is what made
  the prefix ambiguous. Auditing every prefix claim across all 641 species
  found `Pren` was the only one claimed twice. Removed the stray line, and
  added a whole-ontology test so no prefix can be claimed twice again.
- **#112** was misdiagnosed in the issue as auto-generated prefixes squatting.
  They are curated `other prefixes`, and both sides derive legitimately under
  the Klein 2+2 scheme: `Caau` is *Canis aureus* and *Carassius auratus*,
  `Hyam` is *Hyperoodon ampullatus* and *Hybognathus amarus*. The repo already
  had the right mechanism -- `Hymo` gives the global prefix to IPD's
  *Hylobates moloch* and leaves the silver carp a `context only prefixes`
  entry. Applied the same shape: added the two IPD species, moved the fish
  aliases to context-only. Two existing tests encoded the losing resolution
  and were updated to address each fish by its own prefix.
- Bumped 3.33.6 to 3.36.0. Minor rather than patch because bare gene symbols
  and class-only strings change species for downstream callers.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,231 tests; 91% statement coverage).
