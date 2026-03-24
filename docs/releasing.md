# Release Process

## Overview

`mhcgnomes/version.py` is the source of truth for package versioning. Releases
use a hybrid flow:

- local release automation runs strict preflight checks, validates the version,
  builds the package once locally, and pushes an annotated `v<version>` tag
- GitHub Actions rebuilds from that tag, verifies the tag still matches
  `version.py`, checks the generated distributions, and publishes to PyPI using
  trusted publishing

This keeps the existing safety checks from `deploy.py` while removing local
PyPI credentials and local `twine upload`.

## Detailed Plan

1. Keep `version.py` as the only version source.
2. Generate the release tag from `version.py` locally rather than typing it by
   hand.
3. Reuse the same Python helper code for local release automation and CI
   tag/version validation.
4. Trigger production publishing from `push` events on tags matching `v*`.
5. Treat GitHub Actions as the only publisher to PyPI and TestPyPI.
6. Document the maintainer checklist so the release process is explicit and
   reviewable.

## Maintainer TODOs

These are one-time repository setup tasks outside the codebase:

- [ ] Configure a PyPI trusted publisher for the GitHub Actions workflow
  environment named `release`
- [ ] Configure a TestPyPI trusted publisher for the environment named
  `release_testpypi`
- [ ] Decide whether tag pushes matching `v*` should be protected or restricted
  to maintainers
- [ ] Decide whether to add release provenance or signing as a later hardening
  step

## Release Checklist

1. Update `mhcgnomes/version.py` to the new version and commit it on `main`.
2. Run `./deploy.sh --dry-run --fetch` to confirm the repository is clean,
   up-to-date, and ready to release.
3. Run `./deploy.sh --fetch` from a clean local checkout of `main`.
4. Confirm the pushed `v<version>` tag starts the
   `.github/workflows/release.yml` workflow.
5. Verify the workflow succeeds and the new version appears on PyPI.
6. If needed, run `.github/workflows/release_testpypi.yml` manually against an
   existing tag before a production release.

## What `deploy.sh` Enforces

`deploy.sh` still runs the full local test and lint gates before calling
`deploy.py`. `deploy.py` then enforces:

- current branch is `main`
- working tree is clean
- local `main` matches `origin/main`
- the release version parses from `mhcgnomes/version.py`
- the corresponding `v<version>` tag does not already exist
- a local source and wheel build succeeds before any tag is pushed

## Failure Handling

- If the local preflight fails, no tag is created.
- If the CI tag/version validation fails, nothing is published.
- If the build or trusted publish step fails, fix the issue on `main`, bump the
  version, and cut a new tag rather than reusing the failed version number.
