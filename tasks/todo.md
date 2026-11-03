# Public meanings for allele-name annotations; `annotation_cytosolic` (#217)

GitHub issue: #217

## Evidence

- [x] Source every annotation from the authority, verbatim, not from the old
  comment (which guessed "P = same as G?"):
  - N, L, S, C, A, Q: hla.alleles.org naming and suffix pages.
  - G, P: the IMGT/HLA G- and P-group pages. P is coarser than G: same
    protein, not same nucleotides.
  - Ps, Sp: IPD-MHC's NHP nomenclature page.
- [x] Check W. The parser called it a "workshop" prefix. In the names it
  meets, it is IPD-MHC's "allele cannot be defined to a locus/gene yet"
  (Mamu-DRB*W003:07). HLA's workshop "w" was serological (Cw, Bw4), never on
  an allele field.
- [x] Find every `annotation_cystosolic`: `Result`, `Allele`, `Pair` and
  `ResultWithMultipleAlleles`. No sibling repo under ~/code uses it.

## Implementation

- [x] `allele_annotations.annotation_descriptions`: public mapping, each entry
  cited beside it; `valid_functional_annotations` is now derived from it.
- [x] `Allele.annotation_descriptions` (this allele's annotations, in order).
- [x] `Allele.cell_surface_expression`: "absent" (N, S, C, pseudogene by Ps or
  gene curation), "uncertain" (A, Q), "low" (L), or None. This is graded rather
  than the issue's single "in doubt" flag, because L is still on the surface
  (IMGT: low "when compared to normal levels"). A caller wanting the issue's
  set uses `is not None`.
- [x] `annotation_cytosolic` on all four classes. `annotation_cystosolic` is
  defined once, on `Result`, as a deprecated alias.
- [x] Correct the W comments and the copy-pasted `annotation_splice_variant`
  comment.
- [x] Docs: docs/nomenclature.md, doctested.
- [x] File #235: BoLA's splice-variant suffix is `SV`, which is not
  recognized.
- [x] Bump to 3.66.0 (new public API); run `./format.sh`, `./lint.sh`,
  `./test.sh`.
