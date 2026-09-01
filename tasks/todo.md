# Curate the low-resolution (Lr-) swine haplotype series (#162)

## Review

- **The data was reachable after all, and I had said twice that it was not.**
  I checked PMC for Ho et al. 2009 and Hammer et al. 2020 (no full text) and
  read the cohort papers' HTML tables (per-line counts only), then concluded
  the compositions were paywalled. What I never tried was **Europe PMC**, which
  serves the same articles as structured full-text XML:

      https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8362188/fullTextXML

  Tables 1 and 2 are in it in full -- 49 class I and 31 class II rows. The
  supplementary route was a dead end too (PMC gates the download behind an
  interstitial; Europe PMC's supplementaryFiles endpoint serves it, and it
  turned out to hold only primer layouts and frequency figures).

  My greps for "Lr-" had also been finding nothing because the XML uses a
  Unicode hyphen, U+2010.

- **59 haplotypes curated**, 39 class I and 20 class II, every member a
  one-field allele because that is what a group specificity is: `1*04` is
  SLA-1*04XX.

- **The footnotes carry the finding.** Table 1's footnote 5 is "Untyped SLA
  class I locus", and Lr-24.0 and Lr-33.0 show `Blank` **with that footnote**.
  Same word, opposite claim from the plain `Blank` in Lr-23.0. A naive import
  would have recorded two untyped loci as positively absent -- exactly the
  distinction #162 was filed about, confirmed by the source itself.

- **19 rows deliberately left out, each with its reason recorded** in the YAML
  and pinned in a test: composite or unconfirmed names, untyped loci, `+`
  meaning an allele beyond the group, and `/` meaning alternatives. The last
  two need a disjunction member, which is the only part of #162 still open.

- **Cross-validation, unlooked for.** Footnote 3 says Lr-02.0 "did not appear
  to possess an expressed SLA-3 gene", which is the same fact Table 2 of
  PMC5472656 records as Hp-2.0's SLA-3 being *null*. Two independent papers,
  one haplotype at two resolutions, agreeing.

- **Measured:** 0 of 36,752 corpus names change; 0 printed forms fail to parse
  back; 17,129 tests pass, 76 new; no parser warnings from the new entries.
- Bumped to 3.64.0.
