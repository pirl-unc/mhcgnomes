# CLI version and locale-independent data loading

Tracking issues: #95, #96

## Specification

- [x] Add a conventional `mhcgnomes --version` flag backed by the package's existing
      `mhcgnomes.version.__version__` source of truth.
- [x] Add a regression test proving the module CLI prints the program name and package version,
      exits successfully, and does not require an MHC name.
- [x] Decode bundled YAML package data explicitly as UTF-8 so imports do not depend on the host
      locale.
- [x] Add a regression test that imports `mhcgnomes` successfully with UTF-8 mode disabled under
      the C/ASCII locale.
- [x] Bump the patch version for the PR.
- [x] Run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff for minimal scope and document results below.

## Review

- Added argparse's standard version action using the existing package version source of truth.
- Made the bundled YAML loader decode UTF-8 explicitly; `species.yaml` was the first failing file
  under the C/ASCII locale because it contains UTF-8 box-drawing characters in comments.
- Added focused regressions for `--version` and package import with UTF-8 mode disabled under the
  C/ASCII locale.
- Bumped the package from 3.33.4 to 3.33.5.
- Verified `python -m mhcgnomes --version` and the project virtualenv's `mhcgnomes --version` both
  print `mhcgnomes 3.33.5`.
- `./format.sh`: passed (133 files unchanged).
- `./lint.sh`: passed.
- `./test.sh`: passed (15,124 tests, 91% coverage).
