# Canonical DLA-88 allele-field width

Tracking issues: #2, #99

## Specification

- [x] Add a small curated data source for gene-specific first allele-field widths,
      independent of incidental aliases.
- [x] Record the official three-digit DLA-88 first-field convention from IPD-MHC.
- [x] Normalize historical two-digit DLA-88 inputs to the same canonical allele as
      three-digit inputs, with focused parser regressions.
- [x] Preserve wider DLA-88 allele families such as `501` unchanged.
- [x] Make `test.sh` execute pytest through the same Python interpreter used to
      detect optional xdist support, with a regression test for mismatched PATHs.
- [x] Bump the patch version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- Added an explicit, package-data-backed gene-width table instead of encoding
  DLA nomenclature as a synthetic allele alias. Curated entries override the
  widths inferred from real canonical alias targets.
- Verified against the official IPD-MHC DLA catalog, which names the family
  `DLA-88*001:01` and consistently uses three-digit first fields.
- Historical `DLA-88*01:01` now equals and renders as `DLA-88*001:01`; an
  independent regression proves `DLA-88*501:01` is not modified.
- Fixed issue #99 by executing pytest as a module of the same Python used for
  optional xdist detection; the regression supplies deliberately mismatched
  `python` and `pytest` executables on PATH.
- Bumped 3.33.5 to 3.33.6.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,127 tests; 91% statement coverage).
