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
- Resolution order is `DEPLOY_PYTHON`, then the venv interpreter, then
  `sys.executable`. The middle one is the fix: selecting a venv now selects its
  interpreter, not just its `bin` on `PATH`.
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
risk. `checkout`, `setup-python` and `cache` are exercised by `tests.yml` and
`docs.yml` on this PR, so those three are proven by it.

- Bumped to 3.47.1. No library code changes.
