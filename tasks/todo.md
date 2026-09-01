# Release infra: build with the venv, and get the workflows off Node 20

Tracking issues: #101, #94

## Review

### #101 -- deploy.py announced a venv and then built with something else

`build_distributions` used `sys.executable`, which is whatever interpreter
launched `deploy.py`, not the venv the script had just resolved and reported.
The 3.33.6 release reproduced it: "Using venv: .venv", then a build through a
Homebrew Python 3.14 with no `build` module, after lint and 15,127 tests had
passed.

Still live on this machine, which is how I confirmed it rather than trusting
the report:

```
sys.executable  /Users/.../shared-virtual-env/bin/python3
venv python     /Users/.../uv/python/cpython-3.12.6-.../bin/python3.12
same?           False
```

- `Config` carries a `python` field alongside `env`, so the interpreter and the
  environment cannot drift apart.
- Resolution order is `DEPLOY_PYTHON`, then a venv interpreter **that can
  actually build**, then `sys.executable`. See round 2 below: the first version
  of this bullet described preferring the venv unconditionally, which review
  showed would break every release here.
- The build-availability check gets `cfg.env` too; it did not before, so it
  could pass while the real build failed.
- `deploy.py` now prints `Build interpreter: <path>`, so a mismatch is visible
  in the log rather than discovered when `build` turns out to be missing.

### #94 -- Node 20 deprecation

Every `actions/*` pin moved to the **lowest major that runs on Node 24**, read
from each action's own `action.yml` rather than assumed:

| action | was | now | `runs.using` |
|---|---|---|---|
| checkout | v4 | v5 | node24 |
| setup-python | v5 | v6 | node24 |
| upload-artifact | v4 | v6 | node24 |
| download-artifact | v4 | v7 | node24 |
| cache | v4 | v5 | node24 |
| configure-pages | v5 | v6 | node24 |
| deploy-pages | v4 | v5 | node24 |
| upload-pages-artifact | v3 | v5 | composite |

Lowest-that-qualifies rather than latest, deliberately. `download-artifact@v8`
makes a hash mismatch a hard error and migrates to ESM, and both artifact
actions only run on tag push and `workflow_dispatch` -- so PR CI cannot verify
them, and taking the smallest step that clears the deprecation is the lower
risk.

`upload-pages-artifact` is left at **v3**. It is a composite action, so it never
had Node 20 exposure and this issue does not touch it -- and v4.0.0 stops
including dotfiles in the artifact, which would be a silent behaviour change to
the published site bought for no deprecation benefit.

What this PR's own CI proves, and what it does not: `checkout` and
`setup-python` are exercised by `tests.yml` and `docs.yml`. `cache` is used
only in `external-data.yml`, which is path-filtered on `mhcgnomes/**` -- it runs
here only because `version.py` matches, so a later workflow-only change would
leave it unexercised. The artifact actions are not exercised at all.

## Review round 2 (code review, and it caught a regression)

- **My first fix would have broken every release.** It always preferred the
  venv interpreter. But `develop.sh` installs only `.[dev,docs]`, and this
  repo's `.venv` has neither `build` nor `setuptools` nor `wheel`, while the
  launching interpreter has all three:

  ```
  .venv/bin/python  ->  no build, no setuptools, no wheel
  sys.executable    ->  build 1.6.0, setuptools 75.8.0, wheel 0.44.0
  ```

  So `./deploy.sh` would have aborted at the availability check, after lint and
  15,868 tests. I ran `./deploy.sh` a dozen times this session under the old
  behaviour without noticing, because the old behaviour is what works here.
  The fix now prefers the venv **only when it can actually build**, falls back
  otherwise, and prints which and why.
- **Reading `DEPLOY_PYTHON` was redundant and wrong.** `deploy.sh` already does
  `PYTHON_BIN="${DEPLOY_PYTHON:-python3}"` and launches `deploy.py` with it, so
  an explicit override arrives as `sys.executable`. Reading it again let it
  outrank the venv while `cfg.env` still pointed at that venv -- recreating the
  exact mismatch #101 is about. Removed, and a test asserts it stays removed.
- **The probe moved before the cleanup.** `clean_build_artifacts` deletes
  `dist/`, `build/` and `*.egg-info`, including the editable install's, so
  failing after it left the checkout worse off than before the attempt.
- **The probe now checks `setuptools` too.** `--no-isolation` means pyproject's
  `requires = ["setuptools>=61.0", "wheel"]` must already be importable, so
  probing only `build` could pass and the build still fail.
- **A missing interpreter now dies cleanly** instead of raising an uncaught
  `FileNotFoundError` past `__main__`'s `CommandError`-only handler.
- **`upload-pages-artifact` reverted to v3.** It is composite, so it never had
  Node 20 exposure, and v4.0.0 stops including dotfiles in the artifact -- a
  silent change to the published site bought for no deprecation benefit. Read
  only `runs.using` the first time and missed it.
- **`format.sh` could not fix the file this PR edits.** Its `SOURCES` omitted
  `deploy.py` while `lint.sh`'s included it, so the `./format.sh` then
  `./lint.sh` loop AGENTS.md prescribes could not converge. Aligned -- and it
  immediately caught a `%`-format in the new test.
- **`dataclasses.replace`** instead of rebuilding `Config` field by field, so a
  future field cannot be silently dropped.
- **CI caught one of my new tests making the very assumption this PR removes.**
  It asserted the interpreter running the suite can build. True on this
  machine, false on the runner -- the repo's `dev` extra has no `build`, which
  is exactly the environment the change exists to handle. Rewritten against a
  controlled stub, so the suite no longer depends on the runner having build
  tooling at all.
- **11 tests, where there were none.** `resolve_build_python` and
  `interpreter_can_build` are pure enough to test with `tmp_path`; the stub
  venv exits non-zero, since a stub that exits 0 for everything claims it can
  build -- which is how the first version of that test passed wrongly.
- **`docs/releasing.md` gained a "Which interpreter builds" section**, since
  the log line is new and a maintainer needs to know that the fallback is
  normal rather than a failure.
- **Filed rather than fixed: #152.** `AGENTS.md` documents
  `deploy.sh <version>`, which `deploy.py` has no positional argument for -- and
  because `deploy.sh` runs lint and tests first, following that instruction
  burns the full suite before failing on argparse. Two documented release
  processes, one of which does not exist; picking between them is a call about
  how releases should work.
## Review round 3

- **The `upload-pages-artifact` revert was wrong, and my justification was the
  wrong fact.** I said it is composite so it never had Node 20 exposure. It is
  composite -- and its own `action.yml` invokes `actions/upload-artifact@v4`,
  a Node 20 action. v4 nests v4.6.2, also Node 20. **v5 is the only release
  whose nested action runs on Node 24**, so reverting to v3 left the exact gap
  #94 exists to close, in the one workflow that publishes.

  v5 with `include-hidden-files: true` clears Node 20 *and* restores the
  dotfile behaviour v4 changed, so neither concern has to be traded away.
- **`DEPLOY_PYTHON` could not actually force an interpreter.** A capable venv
  silently outranked it, while the failure message told the user to set it.
  Now checked first -- by presence, not by re-reading the path, since
  `deploy.sh` already launches `deploy.py` with it.
- **The build environment did not match the build interpreter.** `cfg.env`
  always names the venv, and I had passed it to a build that may run under the
  launching interpreter -- so `python` and `pip` inside the build would resolve
  to a different interpreter than the one running it. That is #101's drift
  pointed the other way, and it was new: the old code passed no env at all.
  `Config.build_env` now carries the environment that matches `Config.python`.
- **`Path("") .exists()` is `True`** -- it is `PosixPath(".")` -- so the
  existence guard never fired for the empty placeholder it was written for. An
  explicit emptiness check first, then `require_cmd` for relative names so the
  lookup honours the same PATH the build will use.
- **`--dry-run` skipped the one check that matters.** It returns before
  `build_distributions`, so a rehearsal reported success on a checkout that
  cannot build. Split into `check_build_prerequisites`, which both paths call.
- **The probe threw away its diagnostics.** A `build` that is installed but
  broken now reports its actual traceback instead of a fixed message asserting
  the imports are missing.
- **Two tests asserted on source text.** One would have passed a probe with an
  inverted return; the other indexed `source.split('\"\"\"')[2]` and would
  raise `IndexError` on a docstring edit. Replaced with behavioural stubs -- the
  setuptools one uses an interpreter that fails only the two-module import.
- **Tests now cover what the change delivers**, not only its helpers: that
  `Config` carries both the interpreter and its environment, that the probe
  precedes the cleanup, and that `--dry-run` rehearses it.
- Bumped to 3.47.1. No library code changes.
