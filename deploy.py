#!/usr/bin/env python3
"""
deploy.py

Safe deploy/release automation for this repository.

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
  - uv build
  - twine upload
  - git tag v<version> (annotated) + push ONLY that tag

Dry-run:
  - Prints effectful commands but does NOT execute: build/publish/tag/push/fetch.
  - Still runs read-only validations (e.g. tag existence checks, parsing version file).
"""

import argparse
import ast
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence


_VERSION_ALLOWED_RE = re.compile(r"^[0-9][0-9A-Za-z.+-]*$")  # permissive, injection-safe


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str, exit_code: int = 1) -> "NoReturn":
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
    Run a command with side-effects (build/publish/tag/push/fetch).
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


def parse_version_from_python_file(path: Path) -> str:
    if not path.exists():
        die(f"Missing version file: {path}")
    if not path.is_file():
        die(f"Version path is not a regular file: {path}")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        die(f"Failed to read version file {path}: {e}")

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as e:
        die(f"Version file is not valid Python syntax: {path}: {e}")

    found: List[str] = []

    for node in tree.body:
        # __version__ = "1.2.3"
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    value = node.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        found.append(value.value)
                    elif isinstance(value, ast.Str):  # legacy AST
                        found.append(value.s)
                    else:
                        die(f"{path}: __version__ must be a string literal.")
        # __version__: str = "1.2.3"
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "__version__":
                if node.value is None:
                    die(f"{path}: __version__ is annotated but not assigned.")
                value = node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    found.append(value.value)
                elif isinstance(value, ast.Str):
                    found.append(value.s)
                else:
                    die(f"{path}: __version__ must be a string literal.")

    if not found:
        die(f"Failed to find __version__ assignment in {path}.")
    if len(found) > 1:
        die(f"Multiple __version__ assignments found in {path}. Refuse to guess.")

    v = found[0].strip()
    if not v:
        die(f"Parsed empty version from {path}.")
    if not _VERSION_ALLOWED_RE.match(v):
        die(f"Parsed version '{v}' from {path} looks invalid (unexpected characters).")
    return v


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
        die(f"Cannot resolve {remote_refname}. Run: git fetch {cfg.remote} (or rerun with --fetch).")

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


def build_and_publish(cfg: Config, *, cwd: Path) -> None:
    require_cmd("uv", env=cfg.env)
    require_cmd("python3", env=cfg.env)

    note("Cleaning dist/ ...")
    if cfg.dry_run:
        note("rm -rf dist")
    else:
        shutil.rmtree(cwd / "dist", ignore_errors=True)

    note("Building distributions with uv...")
    run_effectful(["uv", "build"], cwd=cwd, dry_run=cfg.dry_run, env=cfg.env)
    ok("Build step complete")

    note("Checking twine availability...")
    run_checked(
        ["python3", "-m", "twine", "--version"],
        cwd=cwd,
        capture_stdout=True,
        capture_stderr=True,
        env=cfg.env,
    )

    dist_dir = cwd / "dist"
    if not dist_dir.exists():
        die("dist/ directory does not exist after build.")
    dist_files = [p for p in sorted(dist_dir.iterdir()) if p.is_file()]
    if not dist_files:
        die("No files in dist/ to publish.")

    note("Publishing with twine...")
    run_effectful(
        ["python3", "-m", "twine", "upload", *[str(p) for p in dist_files]],
        cwd=cwd,
        dry_run=cfg.dry_run,
        env=cfg.env,
    )
    ok("Publish step complete")


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


def resolve_venv_bin(root: Path) -> Optional[Path]:
    for name in (".venv", "venv"):
        candidate = root / name / "bin"
        if (candidate / "python").exists() or (candidate / "python3").exists():
            return candidate
    return None


def build_run_env(venv_bin: Optional[Path]) -> dict[str, str]:
    env = os.environ.copy()
    if venv_bin is not None:
        env["PATH"] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
        env["VIRTUAL_ENV"] = str(venv_bin.parent)
    return env


def parse_args(argv: Sequence[str]) -> Config:
    p = argparse.ArgumentParser(prog="deploy.py")
    p.add_argument("--dry-run", action="store_true", help="Print effectful commands; do not execute them.")
    p.add_argument("--fetch", action="store_true", help="Fetch remote branch before comparing refs.")
    p.add_argument("--version-file", default="mhcgnomes/version.py")
    p.add_argument("--required-branch", default="main")
    p.add_argument("--remote", default="origin")

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
    )


def main(argv: Sequence[str]) -> int:
    cfg = parse_args(argv)
    require_cmd("git")

    root = repo_root()
    venv_bin = resolve_venv_bin(root)
    run_env = build_run_env(venv_bin)

    # Interpret configured paths relative to repo root so deploy.sh works from anywhere.
    cfg = Config(
        version_file=(root / cfg.version_file).resolve(),
        required_branch=cfg.required_branch,
        remote=cfg.remote,
        dry_run=cfg.dry_run,
        fetch=cfg.fetch,
        env=run_env,
    )

    ok(f"Repo root: {root}")
    if venv_bin is not None:
        ok(f"Using venv: {venv_bin.parent}")
    else:
        note("No venv found; using system PATH")

    # Preflight: cheap local checks first.
    ensure_remote_exists(cfg, cwd=root)
    ensure_on_branch(cfg, cwd=root)
    ensure_clean_tree(cwd=root)

    # Now ensure branch is synced with remote (optionally fetching).
    maybe_fetch(cfg, cwd=root)
    ensure_up_to_date(cfg, cwd=root)

    version = parse_version_from_python_file(cfg.version_file)
    tag = f"v{version}"
    validate_tag_name(tag, cwd=root)

    note("Preparing deploy:")
    note(f"  version file: {cfg.version_file}")
    note(f"  version:      {version}")
    note(f"  tag:          {tag}")
    note(f"  branch:       {cfg.required_branch}")
    note(f"  remote:       {cfg.remote}")
    if cfg.dry_run:
        note("  dry-run:      enabled")

    ensure_tag_absent(cfg, tag, cwd=root)

    if cfg.dry_run:
        note("Dry run summary:")
        note("  would run: uv build")
        note("  would run: python3 -m twine upload dist/*")
        note(f"  would run: git tag -a {tag} -m 'Release {tag} ({version})'")
        note(f"  would run: git push {cfg.remote} refs/tags/{tag}")
        ok("Dry run complete")
        return 0

    build_and_publish(cfg, cwd=root)
    tag_and_push(cfg, tag, version, cwd=root)
    ok(f"Deploy complete: {tag}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CommandError as e:
        die(str(e), exit_code=e.returncode)
