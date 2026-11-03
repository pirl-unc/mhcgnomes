# Curated-data warnings go to `warnings`, not stdout

GitHub issue: #213

## Problem

`Parser._find_matching_name_and_parse_alleles` printed two curated-data
problems to stdout with bare `print()`: a `<gene>*Blank` haplotype member
naming a gene the species does not have, and a member that does not parse.
Either would have landed in the middle of a caller's output; `mhcgnomes
--format json` would have stopped producing valid JSON, and callers could not
filter or silence it.

## Plan

- [x] Confirm both sites (`parser.py`, the blank-gene and unparseable-member
  branches) and that no other non-verbose `print()` exists in library code.
- [x] Replace both with `warnings.warn(..., stacklevel=2)`, naming the species
  prefix, the member and the entry, and saying the member is left out.
- [x] Add a test that loads every shipped haplotype and serotype with warnings
  turned into errors, and asserts nothing reaches stdout.
- [x] Unit tests for each condition (warns, prints nothing, keeps the other
  members) and for a known blank gene (recorded, no warning).
- [x] Prove the walk catches a real curation error: adding `NOTAGENE*Blank` to
  SLA `Hp-2.0` makes it fail with the entry named.
- [x] Bump to 3.64.11; run `./format.sh`, `./lint.sh`, `./test.sh`.

## Review

- Both conditions are latent: every shipped haplotype and serotype loads with
  warnings as errors. The walk is what keeps them latent; the warning is what a
  user sees if the data ever regresses.
- The `--verbose` debug prints in `parser.py` are opt-in and unchanged.
