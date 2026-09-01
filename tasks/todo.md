# HLA-Cw16 (#153)

## Review

- **I had the premise backwards, and the source I could not reach settles it.**
  My earlier comment on this issue said the shipped `hla_dictionary.xlsx`
  reports `WHO Assigned Type = "-"` for every `C*16` allele and tops out at
  Cw10, and inferred that HLA-C serology might stop there -- which would have
  put `Cw12`, `Cw14`, `Cw15`, `Cw17` and `Cw18` in doubt too. The dictionary
  reading was right; the inference was wrong.

- **The WHO file was reachable after all.** `hla.alleles.org/wmda/` is a 404,
  but ANHIG/IMGTHLA mirrors the same files:
  `wmda/hla_nom.txt` (3.65.0, 2026-07-14, "author: WHO, Steven G. E. Marsh")
  reads

      Cw;12;20260128;;;      Cw;16;20260128;;;
      Cw;14;20260128;;;      Cw;17;20260128;;;
      Cw;15;20260128;;;      Cw;18;20260128;;;

  All six were assigned on 2026-01-28 by the 2026 HLA Nomenclature Report. The
  dictionary is simply a snapshot from before that date -- it does not
  disagree, it predates.

- **That also explains #156.** Five of the fifteen rows the generator cannot
  reproduce are exactly these C specificities, for the same reason.

- **Two more absences are correct, and now cited.** The same file records
  `Cw;11;19871121;19911114;1;Sequence error` -- assigned then withdrawn -- and
  has no `Cw13` line at all. Both now have a test.

- **Members from the authority, not from the shape of the neighbours.**
  `wmda/rel_ser_ser.txt` reads `Cw;16;;1601/1602`, and `rel_dna_ser.txt` maps
  `C*16:01 -> 1601` and `C*16:02 -> 1602`. The same file associates ~240
  further `C*16` alleles with the broad specificity; those are left out for the
  same reason the neighbouring rows leave out their own hundreds.

- **Regenerated `serotypes_generated.yaml`** so the two files still match: the
  generator carries forward rows the dictionary does not support, so `Cw16`
  survives a re-run exactly as `Cw15` does.

- **Measured:** 0 of 36,752 corpus names change -- `HLA-Cw16` is not in any
  bundled corpus, which is why the hitlist scan found it and these did not.
  16,373 tests pass.
- Bumped to 3.54.0.
