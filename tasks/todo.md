# Record the turkey negative, and that a search summary invented it (#131)

## Review

- **A web search produced a plausible-looking answer, and it was wrong.** For
  `Mega` (*Meleagris gallopavo*) the summary asserted that turkey class I genes
  use "Mega-Ia1" and "Mega-Ia2". Both primary papers say otherwise:
  "Defining the turkey MHC: sequence and genes of the B locus" (PMID 19864609)
  and its class I/IIB sequel (PMID 21710346) describe the turkey MHC as
  **MHC-B** and **MHC-Y** -- the chicken system -- and neither writes `Mega-`.

- **GenBank agrees.** Of 35 turkey MHC records, **zero** contain "Mega-". The
  gene labels are `MHC-B` (10), `IIb1`, `IIb2`, `IIb3`, `DMB2`. Same pattern as
  the peafowl, deposited under the chicken `B-LB` nomenclature.

- **So `Mega` moves from silence to evidence against**, joining `Pacr` and
  `Xetr` in the canary test. Three of the five remaining unknowns now have a
  positive reason rather than an absence of hits.

- **Third time this issue.** A summary of the IPD group list once reported
  "CLA = cat" and "CeLA = deer", both wrong. The mhcseqs registry cites the
  de Groot report for six `_LA` codes it does not contain. And now this. The
  protocol that caught all three is the same: use search to find candidate
  sources, then read each one verbatim before believing it.

- **Verified:** 16,439 tests pass; no data changed, so no corpus measurement
  applies.
- Bumped to 3.59.2.
