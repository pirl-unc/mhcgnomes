#!/usr/bin/env python3
"""
deploy.py

Safe release-tag automation for this repository.

Policy (enforced):
  - Only deploy from REQUIRED_BRANCH (default: main)
  - Require a clean working tree (no staged/unstaged/untracked changes)
  - Require local REQUIRED_BRANCH to match REMOTE/REQUIRED_BRANCH
    (optionally after fetching, if --fetch is provided)
  - Use version already committed in VERSION_FILE (default: mhcgnomes/version.py)
  - Refuse to proceed if the tag already exists locally or on the remote

Does (in this order):
  - preflight checks (repo/branch/clean)
  - (optional) fetch remote branch
  - confirm local up-to-date with remote
  - python -m build
  - git tag v<version> (annotated) + push ONLY that tag

Publishing is handled by GitHub Actions after the tag push.

Dry-run:
  - Prints effectful commands but does NOT execute: build/tag/push/fetch.
  - Still runs read-only validations (e.g. tag existence checks, parsing version file).
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import NoReturn, Optional

from release_utils import ReleaseError, parse_version_from_python_file, tag_for_version


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str, exit_code: int = 1) -> NoReturn:
    eprint(f"ERROR: {msg}")
    raise SystemExit(exit_code)


def note(msg: str) -> None:
    eprint(f"==> {msg}")


def ok(msg: str) -> None:
    eprint(f"OK: {msg}")


def shell_join(cmd: Sequence[str]) -> str:
    return " ".join(shlex.quote(c) for c in cmd)


@dataclass(frozen=True)
class Config:
    version_file: Path
    required_branch: str
    remote: str
    dry_run: bool
    fetch: bool
    env: Optional[dict[str, str]]
    # The interpreter that runs the build. Not necessarily the one that goes
    # with `env`: `env` always names the venv, while the build falls back to the
    # launching interpreter when the venv cannot build. See issue #101.
    python: str
    # The environment for the build subprocess, which must match `python`.
    # `env` (venv PATH + VIRTUAL_ENV) when the venv is the build interpreter,
    # None otherwise -- passing the venv's environment to a different
    # interpreter is the same drift, pointed the other way.
    build_env: Optional[dict[str, str]]
    # How long to wait for the pushed tag to appear on PyPI, and whether to
    # look at all. See await_pypi_publication and issue #83.
    pypi_project: str
    pypi_timeout: float
    check_pypi: bool


class CommandError(RuntimeError):
    def __init__(self, cmd: Sequence[str], returncode: int) -> None:
        super().__init__(f"Command failed (exit={returncode}): {shell_join(cmd)}")
        self.cmd = list(cmd)
        self.returncode = returncode


def require_nonempty(label: str, value: str) -> None:
    if not label:
        die("Internal error: label is empty in require_nonempty")
    if not value:
        die(f"{label} must not be empty")


def require_cmd(cmd: str, *, env: Optional[dict[str, str]] = None) -> None:
    require_nonempty("command", cmd)
    path = env.get("PATH") if env else None
    if shutil.which(cmd, path=path) is None:
        die(f"Missing required command: {cmd}")


def run_checked(
    cmd: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    capture_stdout: bool = False,
    capture_stderr: bool = False,
    env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """
    Run a command (read-only checks, queries). Always executes.
    Always uses shell=False to avoid quoting/injection bugs.
    """
    note(shell_join(cmd))
    stdout = subprocess.PIPE if capture_stdout else None
    stderr = subprocess.PIPE if capture_stderr else None
    cp = subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd is not None else None,
        check=False,
        text=True,
        stdout=stdout,
        stderr=stderr,
        env=env,
    )
    if cp.returncode != 0:
        if cp.stdout:
            eprint(cp.stdout.rstrip("\n"))
        if cp.stderr:
            eprint(cp.stderr.rstrip("\n"))
        raise CommandError(cmd, cp.returncode)
    return cp


def run_effectful(
    cmd: Sequence[str], *, cwd: Path, dry_run: bool, env: Optional[dict[str, str]] = None
) -> None:
    """
    Run a command with side-effects (build/tag/push/fetch).
    In dry-run mode, only prints.
    """
    note(shell_join(cmd))
    if dry_run:
        return
    cp = subprocess.run(list(cmd), cwd=str(cwd), env=env)
    if cp.returncode != 0:
        raise CommandError(cmd, cp.returncode)


def git_output(cmd: Sequence[str], *, cwd: Path) -> str:
    cp = run_checked(cmd, cwd=cwd, capture_stdout=True, capture_stderr=True)
    assert cp.stdout is not None
    return cp.stdout.strip()


def git_succeeds(cmd: Sequence[str], *, cwd: Path) -> bool:
    cp = subprocess.run(
        list(cmd),
        cwd=str(cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return cp.returncode == 0


def repo_root() -> Path:
    require_cmd("git")
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    except subprocess.CalledProcessError:
        die("Not inside a git repository.")
    if not out:
        die("Failed to determine repository root.")
    root = Path(out)
    if not root.is_dir():
        die(f"Resolved repo root is not a directory: {root}")
    return root


def current_branch(*, cwd: Path) -> str:
    cp = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if cp.returncode != 0:
        return ""
    return (cp.stdout or "").strip()


def ensure_on_branch(cfg: Config, *, cwd: Path) -> None:
    branch = current_branch(cwd=cwd)
    if not branch:
        die(
            "Detached HEAD (or unable to determine branch). "
            f"Check out '{cfg.required_branch}' and retry."
        )
    if branch != cfg.required_branch:
        die(f"Deploys must be run from '{cfg.required_branch}'. Current branch: '{branch}'.")
    ok(f"On branch '{cfg.required_branch}'")


def ensure_clean_tree(*, cwd: Path) -> None:
    status = git_output(["git", "status", "--porcelain=v1"], cwd=cwd)
    if status:
        eprint(status)
        die("Working tree not clean. Commit or stash changes before deploying.")
    ok("Working tree is clean")


def ensure_remote_exists(cfg: Config, *, cwd: Path) -> None:
    require_nonempty("remote", cfg.remote)
    if not git_succeeds(["git", "remote", "get-url", cfg.remote], cwd=cwd):
        die(f"Remote '{cfg.remote}' not found.")
    ok(f"Remote '{cfg.remote}' exists")


def validate_tag_name(tag: str, *, cwd: Path) -> None:
    require_nonempty("tag", tag)
    if not git_succeeds(
        ["git", "check-ref-format", "--allow-onelevel", f"refs/tags/{tag}"], cwd=cwd
    ):
        die(f"Tag '{tag}' is not a valid git tag name.")


def ensure_tag_absent(cfg: Config, tag: str, *, cwd: Path) -> None:
    validate_tag_name(tag, cwd=cwd)

    if git_succeeds(
        ["git", "show-ref", "--tags", "--quiet", "--verify", f"refs/tags/{tag}"], cwd=cwd
    ):
        die(f"Tag '{tag}' already exists locally.")

    if git_succeeds(
        ["git", "ls-remote", "--exit-code", "--tags", cfg.remote, f"refs/tags/{tag}"], cwd=cwd
    ):
        die(f"Tag '{tag}' already exists on {cfg.remote}.")

    ok(f"Tag '{tag}' does not exist (local or {cfg.remote})")


def maybe_fetch(cfg: Config, *, cwd: Path) -> None:
    if not cfg.fetch:
        note(
            f"Not fetching remotes (default). If refs are stale, rerun with --fetch or run: "
            f"git fetch {cfg.remote}"
        )
        return
    note(f"Fetching '{cfg.remote}/{cfg.required_branch}' (because --fetch was provided)...")
    run_effectful(
        ["git", "fetch", "--prune", cfg.remote, cfg.required_branch],
        cwd=cwd,
        dry_run=cfg.dry_run,
        env=cfg.env,
    )
    ok("Fetch complete")


def ensure_up_to_date(cfg: Config, *, cwd: Path) -> None:
    remote_refname = f"{cfg.remote}/{cfg.required_branch}"
    if not git_succeeds(["git", "rev-parse", "--verify", remote_refname], cwd=cwd):
        die(
            f"Cannot resolve {remote_refname}. Run: git fetch {cfg.remote} (or rerun with --fetch)."
        )

    local_ref = git_output(["git", "rev-parse", "--verify", "HEAD"], cwd=cwd)
    remote_ref = git_output(["git", "rev-parse", "--verify", remote_refname], cwd=cwd)
    base = git_output(["git", "merge-base", "HEAD", remote_refname], cwd=cwd)

    if local_ref != remote_ref:
        if base == local_ref:
            die(
                f"Local {cfg.required_branch} is BEHIND {remote_refname}. "
                f"Run: git pull --ff-only {cfg.remote} {cfg.required_branch}"
            )
        if base == remote_ref:
            die(
                f"Local {cfg.required_branch} is AHEAD of {remote_refname} (unpushed commits). "
                f"Push first: git push {cfg.remote} {cfg.required_branch}"
            )
        die(
            f"Local {cfg.required_branch} has DIVERGED from {remote_refname}. "
            f"Rebase/merge, push, then retry."
        )

    ok(f"Local {cfg.required_branch} matches {remote_refname}")


def clean_build_artifacts(*, cwd: Path, dry_run: bool) -> None:
    paths_to_remove = [
        cwd / "dist",
        cwd / "build",
        *sorted(cwd.glob("*.egg-info")),
    ]

    note("Cleaning build artifacts ...")
    for path in paths_to_remove:
        note(f"rm -rf {path}")
        if dry_run:
            continue
        shutil.rmtree(path, ignore_errors=True)


def check_build_prerequisites(cfg: Config) -> None:
    """
    Can the resolved interpreter actually build? Separate from
    build_distributions so `--dry-run` runs it too: a dry run exists to rehearse
    the release, and reporting success on a checkout that cannot build is the
    #101 experience in miniature. Also runs before anything is deleted --
    clean_build_artifacts removes dist/, build/ and *.egg-info, including the
    editable install's, so failing after it leaves the checkout worse off.
    """
    build_python = cfg.python
    note(f"Checking build availability with {build_python}...")
    # Not `Path(x).exists()` alone: Path("") is PosixPath("."), which exists, so
    # an empty interpreter would slip straight past. require_cmd does the
    # env-aware PATH lookup, so a bare name resolves against the same PATH the
    # build will run with.
    if not build_python:
        die("No build interpreter was resolved.")
    if Path(build_python).is_absolute():
        if not Path(build_python).is_file():
            die(f"Build interpreter does not exist: {build_python}")
    else:
        require_cmd(build_python, env=cfg.build_env)

    can_build, why_not = interpreter_can_build(build_python, env=cfg.build_env)
    if not can_build:
        die(
            f"{build_python} cannot run `python -m build --no-isolation`, which needs "
            f"both 'build' and 'setuptools' importable.\n{why_not}\n"
            f"Install them there:\n"
            f"    {build_python} -m pip install build setuptools wheel\n"
            f"or set DEPLOY_PYTHON to an interpreter that has them."
        )
    ok(f"{build_python} can build")


def build_distributions(cfg: Config, *, cwd: Path) -> None:
    build_python = cfg.python
    check_build_prerequisites(cfg)
    clean_build_artifacts(cwd=cwd, dry_run=cfg.dry_run)

    note(f"Building distributions with {build_python} -m build (no isolation)...")
    # Deliberately not cfg.env. That environment names the venv -- VIRTUAL_ENV
    # set, its bin prepended to PATH -- and when the build falls back to the
    # launching interpreter the two disagree, so `python` and `pip` inside the
    # build would resolve to a different interpreter than the one running it.
    # That is the drift #101 is about, pointed the other way.
    run_effectful(
        [build_python, "-m", "build", "--no-isolation"],
        cwd=cwd,
        env=cfg.build_env,
        dry_run=cfg.dry_run,
    )
    ok("Build step complete")

    dist_dir = cwd / "dist"
    if not dist_dir.exists():
        die("dist/ directory does not exist after build.")
    dist_files = [p for p in sorted(dist_dir.iterdir()) if p.is_file()]
    if not dist_files:
        die("No files in dist/ after build.")
    ok("Distribution artifacts created")


def tag_and_push(cfg: Config, tag: str, version: str, *, cwd: Path) -> None:
    validate_tag_name(tag, cwd=cwd)
    require_nonempty("version", version)

    note(f"Creating annotated tag {tag}...")
    run_effectful(
        ["git", "tag", "-a", tag, "-m", f"Release {tag} ({version})"],
        cwd=cwd,
        dry_run=cfg.dry_run,
        env=cfg.env,
    )
    ok("Tag created")

    note(f"Pushing tag {tag} to {cfg.remote}...")
    run_effectful(
        ["git", "push", cfg.remote, f"refs/tags/{tag}"],
        cwd=cwd,
        dry_run=cfg.dry_run,
        env=cfg.env,
    )
    ok("Tag pushed")


# What a PyPI lookup can tell us. "absent" is the only one that means the
# release failed; "unknown" means the question could not be asked.
PYPI_PRESENT = "present"
PYPI_ABSENT = "absent"
PYPI_UNKNOWN = "unknown"


def pypi_released_versions(project: str, *, timeout: float = 10.0) -> Optional[set[str]]:
    """
    Every version PyPI has for this project, or None if it could not be asked.

    None and the empty set are different answers and the caller must not
    conflate them: a network failure is not evidence that a release is missing.
    """
    url = f"https://pypi.org/pypi/{project}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    releases = payload.get("releases")
    if not isinstance(releases, dict):
        return None
    return set(releases)


def await_pypi_publication(cfg: Config, version: str) -> str:
    """
    Wait for the pushed tag to become a PyPI release, and say what happened.

    deploy.py used to end by printing "GitHub Actions will build and publish
    this tag to PyPI", which has been false since #83: the trusted-publisher
    exchange fails with `invalid-publisher`, the workflow stops, and the tag
    sits on GitHub with nothing behind it. The script reported success anyway,
    so "done means merged AND deployed" was being satisfied on paper by a
    sentence rather than by a release.

    Returns one of PYPI_PRESENT / PYPI_ABSENT / PYPI_UNKNOWN.
    """
    deadline = time.monotonic() + cfg.pypi_timeout
    unreachable = False
    attempt = 0
    while True:
        versions = pypi_released_versions(cfg.pypi_project)
        attempt += 1
        if versions is None:
            unreachable = True
        elif version in versions:
            return PYPI_PRESENT
        else:
            unreachable = False
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        if attempt == 1:
            note(
                f"Waiting up to {cfg.pypi_timeout:.0f}s for {cfg.pypi_project} "
                f"{version} to appear on PyPI..."
            )
        time.sleep(min(10.0, remaining))
    return PYPI_UNKNOWN if unreachable else PYPI_ABSENT


def report_pypi_outcome(cfg: Config, version: str, tag: str, *, cwd: Path) -> int:
    """
    Turn the lookup into an exit code and, when it failed, into instructions.

    Exit 3 rather than 1 so a caller can tell "the release did not land" from
    "the script could not run". The tag is already pushed at this point, so the
    instructions must not be "run deploy.sh again" -- that fails on the
    existing tag, which is the trap #152 was about.
    """
    if not cfg.check_pypi:
        note("Skipping the PyPI check (--skip-pypi-check).")
        note(f"Nothing has confirmed that {version} was published.")
        return 0

    outcome = await_pypi_publication(cfg, version)
    if outcome == PYPI_PRESENT:
        ok(f"{cfg.pypi_project} {version} is on PyPI")
        return 0

    artifacts = sorted(str(p) for p in (cwd / "dist").glob(f"*{version}*"))
    if outcome == PYPI_UNKNOWN:
        note(f"Could not reach PyPI to confirm {version}. The tag {tag} is pushed.")
        note(f"Check https://pypi.org/project/{cfg.pypi_project}/ before calling this released.")
        return 0

    eprint(f"ERROR: {tag} is pushed but PyPI still has no {version}.")
    eprint("This is issue #83: the release workflow's trusted-publisher exchange fails")
    eprint("with `invalid-publisher`, so the tag lands on GitHub and nothing reaches PyPI.")
    eprint("")
    eprint("Do NOT re-run deploy.sh -- the tag exists now, and it will stop on that.")
    if artifacts:
        eprint("Upload what was already built:")
        eprint(f"  python -m twine upload {' '.join(artifacts)}")
    else:
        eprint(f"No dist/ artifacts for {version} were found to upload.")
    return 3


def resolve_venv_bin(root: Path) -> Optional[Path]:
    for name in (".venv", "venv"):
        candidate = root / name / "bin"
        if (candidate / "python").exists() or (candidate / "python3").exists():
            return candidate
    return None


def venv_python(venv_bin: Optional[Path]) -> Optional[Path]:
    """The interpreter inside the venv whose bin directory this is."""
    if venv_bin is None:
        return None
    for name in ("python", "python3"):
        candidate = venv_bin / name
        if candidate.exists():
            return candidate
    return None


def interpreter_can_build(python: str, env: Optional[dict[str, str]] = None) -> tuple[bool, str]:
    """
    Can this interpreter run `python -m build --no-isolation`, and if not, why?

    Both imports matter. `--no-isolation` means the build backend is not
    provisioned for us, so pyproject's `requires = ["setuptools>=61.0", "wheel"]`
    has to already be importable here. Probing only `build` would pass on an
    environment that then fails inside the build.
    """
    try:
        result = subprocess.run(
            [python, "-c", "import build, setuptools"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
    except OSError as exc:
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    # Keep the traceback. A `build` that is installed but broken -- a stale
    # .pth, an incompatible `packaging` -- exits non-zero for a reason the
    # fixed message would otherwise throw away.
    return False, (result.stderr or result.stdout or "").strip()


def resolve_build_python(
    venv_bin: Optional[Path], env: Optional[dict[str, str]]
) -> tuple[str, str]:
    """
    The interpreter that will run the build, and a phrase explaining the choice.

    Issue #101 was that deploy.py resolved a venv, said so, and then built with
    `sys.executable` -- whatever launched it. The obvious fix, always preferring
    the venv, is worse: develop.sh installs only `.[dev,docs]`, which has no
    `build` and no `setuptools`, so the venv usually cannot build at all. That
    would turn a working release into one that aborts after lint and the full
    test suite.

    So prefer the venv *when it can actually build*, fall back otherwise, and
    return the reason either way so the log can say which and why. Note there is
    no DEPLOY_PYTHON check here: deploy.sh launches deploy.py with it
    (`PYTHON_BIN="${DEPLOY_PYTHON:-python3}"`), so an explicit override already
    arrives as sys.executable.
    """
    fallback = sys.executable or "python3"
    # deploy.sh runs `PYTHON_BIN="${DEPLOY_PYTHON:-python3}"; "$PYTHON_BIN" deploy.py`,
    # so when the variable is set the launching interpreter *is* the requested
    # one. Checking for its presence -- rather than re-reading the path -- lets
    # an explicit request outrank a capable venv, which it must: it is the only
    # way to force an interpreter, and the failure message points at it.
    if os.environ.get("DEPLOY_PYTHON"):
        return fallback, "DEPLOY_PYTHON"
    candidate = venv_python(venv_bin)
    if candidate is None:
        return fallback, "launching interpreter; no project venv found"
    if interpreter_can_build(str(candidate), env=env)[0]:
        return str(candidate), "project venv"
    return (
        fallback,
        f"launching interpreter; {candidate} cannot import build and setuptools",
    )


def build_run_env(venv_bin: Optional[Path]) -> dict[str, str]:
    env = os.environ.copy()
    if venv_bin is not None:
        env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
        env["VIRTUAL_ENV"] = str(venv_bin.parent)
    return env


def parse_args(argv: Sequence[str]) -> Config:
    p = argparse.ArgumentParser(prog="deploy.py")
    p.add_argument(
        "--dry-run", action="store_true", help="Print effectful commands; do not execute them."
    )
    p.add_argument(
        "--fetch", action="store_true", help="Fetch remote branch before comparing refs."
    )
    p.add_argument("--version-file", default="mhcgnomes/version.py")
    p.add_argument("--required-branch", default="main")
    p.add_argument("--remote", default="origin")
    p.add_argument("--pypi-project", default="mhcgnomes")
    p.add_argument(
        "--pypi-timeout",
        type=float,
        default=300.0,
        help="Seconds to wait for the release to appear on PyPI (default 300).",
    )
    p.add_argument(
        "--skip-pypi-check",
        action="store_true",
        help="Push the tag without checking whether PyPI received the release.",
    )

    ns = p.parse_args(list(argv))
    require_nonempty("--required-branch", ns.required_branch)
    require_nonempty("--remote", ns.remote)

    return Config(
        version_file=Path(ns.version_file),
        required_branch=ns.required_branch,
        remote=ns.remote,
        dry_run=bool(ns.dry_run),
        fetch=bool(ns.fetch),
        env=None,
        # Placeholders. main() resolves the real ones with resolve_build_python
        # once the repo root and venv are known.
        python="",
        build_env=None,
        pypi_project=ns.pypi_project,
        pypi_timeout=float(ns.pypi_timeout),
        check_pypi=not bool(ns.skip_pypi_check),
    )


def main(argv: Sequence[str]) -> int:
    cfg = parse_args(argv)
    require_cmd("git")

    root = repo_root()
    venv_bin = resolve_venv_bin(root)
    run_env = build_run_env(venv_bin)
    build_python, build_python_reason = resolve_build_python(venv_bin, run_env)
    build_env = run_env if build_python_reason == "project venv" else None

    # Interpret configured paths relative to repo root so deploy.sh works from
    # anywhere. dataclasses.replace rather than a field-by-field rebuild, so a
    # future Config field cannot be silently dropped here.
    cfg = replace(
        cfg,
        version_file=(root / cfg.version_file).resolve(),
        env=run_env,
        python=build_python,
        build_env=build_env,
    )

    ok(f"Repo root: {root}")
    if venv_bin is not None:
        ok(f"Using venv: {venv_bin.parent}")
    else:
        note("No venv found; using system PATH")
    # Name the interpreter that will actually run the build, and why it was
    # chosen. The bug in #101 was not that the wrong one was picked, it was that
    # the log said one thing and the build did another.
    ok(f"Build interpreter: {cfg.python} ({build_python_reason})")

    # Preflight: cheap local checks first.
    ensure_remote_exists(cfg, cwd=root)
    ensure_on_branch(cfg, cwd=root)
    ensure_clean_tree(cwd=root)

    # Now ensure branch is synced with remote (optionally fetching).
    maybe_fetch(cfg, cwd=root)
    ensure_up_to_date(cfg, cwd=root)

    try:
        version = parse_version_from_python_file(cfg.version_file)
    except ReleaseError as exc:
        die(str(exc))
    tag = tag_for_version(version)
    validate_tag_name(tag, cwd=root)

    note("Preparing release tag:")
    note(f"  version file: {cfg.version_file}")
    note(f"  version:      {version}")
    note(f"  tag:          {tag}")
    note(f"  branch:       {cfg.required_branch}")
    note(f"  remote:       {cfg.remote}")
    if cfg.dry_run:
        note("  dry-run:      enabled")

    ensure_tag_absent(cfg, tag, cwd=root)

    if cfg.dry_run:
        # Rehearse the part that actually breaks releases.
        check_build_prerequisites(cfg)
        note("Dry run summary:")
        note(f"  would run: {cfg.python} -m build --no-isolation")
        note(f"  would run: git tag -a {tag} -m 'Release {tag} ({version})'")
        note(f"  would run: git push {cfg.remote} refs/tags/{tag}")
        if cfg.check_pypi:
            note(f"  would then wait up to {cfg.pypi_timeout:.0f}s for PyPI to have {version}")
        ok("Dry run complete")
        return 0

    build_distributions(cfg, cwd=root)
    tag_and_push(cfg, tag, version, cwd=root)
    ok(f"Release tag pushed: {tag}")
    return report_pypi_outcome(cfg, version, tag, cwd=root)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CommandError as e:
        die(str(e), exit_code=e.returncode)
