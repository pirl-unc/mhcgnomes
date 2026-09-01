# Make deploy.sh tell the truth about whether the release shipped (#83)

## Review

- **The trusted-publisher configuration is still the user's to do** -- it needs
  pypi.org access. What was fixable here is the second half of #83, quoted from
  the issue itself: *"`./deploy.sh` looks like it succeeds (it pushes the tag)
  but the package never lands on PyPI -- violates the 'done = merged AND
  deployed' Golden Rule silently."*

- **The script ended with a claim, not a check.**

      ok(f"Release tag pushed: {tag}")
      note("GitHub Actions will build and publish this tag to PyPI.")

  That second line has been false for every release since #83 was filed. Golden
  Rule 3 was being satisfied by a sentence.

- **Three outcomes, not two.** A network failure is not evidence that a release
  is missing, so `pypi_released_versions` returns `None` for "could not ask"
  and a set for "asked". Conflating them with an empty set would fail every
  offline deploy. Present -> exit 0, unknown -> exit 0 with no claim of
  success, absent -> exit 3.

- **Exit 3, not 1**, so a caller can tell "the release did not land" from "the
  script could not run".

- **The failure message cannot say "re-run deploy.sh".** The tag is pushed by
  then, so a re-run stops on `ensure_tag_absent` -- the trap #152 was about. It
  prints the `twine upload` line for the artifacts already in `dist/` instead.

- **Verified:** 14 new tests; breaking either mechanism (returning an empty set
  for an unreachable index, or exiting 0 on absent) fails 5 of them. 16,387
  tests pass.
- Bumped to 3.55.0.
