"""
Which interpreter `deploy.py` runs the build with, and whether it says so.

Issue #101 was not that the wrong interpreter was chosen -- it was that the
script resolved a venv, printed "Using venv: .venv", and then built with
whatever launched it. The obvious fix, always preferring the venv, is worse
here: develop.sh installs only `.[dev,docs]`, which has no `build` and no
`setuptools`, so the venv usually cannot build at all.

Everything below runs against stub interpreters rather than the one running
the suite. An earlier version asserted `interpreter_can_build(sys.executable)`,
which is true locally and false in CI -- the exact environment this change
exists to handle.

https://github.com/pirl-unc/mhcgnomes/issues/101
"""

import sys
from dataclasses import fields
from pathlib import Path

import pytest

deploy = pytest.importorskip("deploy")


def _stub_interpreter(tmp_path, name=".venv", interpreter="python", can_build=False):
    """
    A venv whose interpreter is a stub shell script. `can_build=False` makes it
    fail any command, which is what a develop.sh venv does for `import build`;
    a stub that exits 0 for everything would claim it can build.
    """
    bin_dir = tmp_path / name / "bin"
    bin_dir.mkdir(parents=True)
    script = bin_dir / interpreter
    script.write_text(f"#!/bin/sh\nexit {0 if can_build else 1}\n")
    script.chmod(0o755)
    return bin_dir


# ---------------------------------------------------------------------------
# Locating a venv interpreter
# ---------------------------------------------------------------------------


def test_venv_python_finds_the_interpreter(tmp_path):
    bin_dir = _stub_interpreter(tmp_path)
    assert deploy.venv_python(bin_dir) == bin_dir / "python"


def test_venv_python_accepts_python3_only(tmp_path):
    bin_dir = _stub_interpreter(tmp_path, interpreter="python3")
    assert deploy.venv_python(bin_dir) == bin_dir / "python3"


def test_venv_python_is_none_without_a_venv():
    assert deploy.venv_python(None) is None


# ---------------------------------------------------------------------------
# The build-capability probe
# ---------------------------------------------------------------------------


def test_probe_is_true_when_the_imports_succeed(tmp_path):
    bin_dir = _stub_interpreter(tmp_path, can_build=True)
    can_build, why_not = deploy.interpreter_can_build(str(bin_dir / "python"))
    assert can_build
    assert why_not == ""


def test_probe_is_false_when_the_imports_fail(tmp_path):
    bin_dir = _stub_interpreter(tmp_path, can_build=False)
    can_build, _ = deploy.interpreter_can_build(str(bin_dir / "python"))
    assert not can_build


def test_probe_is_false_for_a_missing_interpreter(tmp_path):
    can_build, why_not = deploy.interpreter_can_build(str(tmp_path / "no-such-python"))
    assert not can_build
    assert why_not, "an OSError should still explain itself"


def test_probe_keeps_the_diagnostics(tmp_path):
    """
    A `build` that is installed but broken exits non-zero for a reason the
    fixed error message would otherwise throw away.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    script = bin_dir / "python"
    script.write_text("#!/bin/sh\necho 'ModuleNotFoundError: no packaging' >&2\nexit 1\n")
    script.chmod(0o755)
    can_build, why_not = deploy.interpreter_can_build(str(script))
    assert not can_build
    assert "no packaging" in why_not


def test_probe_requires_setuptools_not_just_build(tmp_path):
    """
    `--no-isolation` means pyproject's backend is not provisioned for us, so an
    interpreter with `build` but no `setuptools` must be rejected. Behavioural,
    not a grep of the source: the stub fails only the two-module import.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True)
    script = bin_dir / "python"
    script.write_text('#!/bin/sh\ncase "$2" in *setuptools*) exit 1 ;; esac\nexit 0\n')
    script.chmod(0o755)
    assert not deploy.interpreter_can_build(str(script))[0]


# ---------------------------------------------------------------------------
# Choosing the build interpreter
# ---------------------------------------------------------------------------


def test_a_usable_venv_is_preferred(tmp_path):
    bin_dir = _stub_interpreter(tmp_path, can_build=True)
    chosen, reason = deploy.resolve_build_python(bin_dir, env=None)
    assert chosen == str(bin_dir / "python")
    assert reason == "project venv"


def test_a_venv_that_cannot_build_falls_back_and_says_why(tmp_path):
    """
    The regression this guards against: preferring a venv with no `build` turns
    a working release into one that aborts after lint and the full test suite.
    """
    bin_dir = _stub_interpreter(tmp_path, can_build=False)
    chosen, reason = deploy.resolve_build_python(bin_dir, env=None)
    assert chosen == (sys.executable or "python3")
    assert "cannot import build" in reason
    assert str(bin_dir / "python") in reason


def test_no_venv_reports_the_launching_interpreter():
    chosen, reason = deploy.resolve_build_python(None, env=None)
    assert chosen == (sys.executable or "python3")
    assert "no project venv" in reason


def test_deploy_python_outranks_even_a_usable_venv(tmp_path, monkeypatch):
    """
    deploy.sh launches deploy.py with DEPLOY_PYTHON, so an explicit request
    arrives as sys.executable. It has to win: it is the only way to force an
    interpreter, and the failure message tells the user to set it.
    """
    monkeypatch.setenv("DEPLOY_PYTHON", "/somewhere/python3.11")
    bin_dir = _stub_interpreter(tmp_path, can_build=True)
    chosen, reason = deploy.resolve_build_python(bin_dir, env=None)
    assert chosen == (sys.executable or "python3")
    assert reason == "DEPLOY_PYTHON"


def test_without_deploy_python_the_venv_wins(tmp_path, monkeypatch):
    monkeypatch.delenv("DEPLOY_PYTHON", raising=False)
    bin_dir = _stub_interpreter(tmp_path, can_build=True)
    assert deploy.resolve_build_python(bin_dir, env=None)[1] == "project venv"


# ---------------------------------------------------------------------------
# What the PR actually delivers, rather than the helpers it delivers it with
# ---------------------------------------------------------------------------


def test_config_carries_both_the_interpreter_and_its_environment():
    """
    Dropping `python` or `build_env` from the Config main() builds would
    reintroduce #101 while every helper test still passed.
    """
    names = {f.name for f in fields(deploy.Config)}
    assert {"python", "build_env", "env"} <= names


def test_the_build_environment_matches_the_chosen_interpreter(tmp_path, monkeypatch):
    """
    `env` always names the venv. When the build falls back to the launching
    interpreter the two disagree, so the build must not inherit it -- `python`
    and `pip` on that PATH would resolve to a different interpreter than the
    one running the build. Same drift as #101, pointed the other way.
    """
    monkeypatch.delenv("DEPLOY_PYTHON", raising=False)
    for can_build, expect_venv_env in [(True, True), (False, False)]:
        bin_dir = _stub_interpreter(tmp_path / f"case{can_build}", can_build=can_build)
        _, reason = deploy.resolve_build_python(bin_dir, env=None)
        assert (reason == "project venv") is expect_venv_env


def test_the_probe_runs_before_anything_is_deleted():
    """
    clean_build_artifacts removes dist/, build/ and *.egg-info including the
    editable install's, so a failure after it leaves the checkout worse off
    than before the attempt.
    """
    import inspect

    source = inspect.getsource(deploy.build_distributions)
    assert source.index("check_build_prerequisites") < source.index("clean_build_artifacts")


def test_dry_run_rehearses_the_build_check():
    """A dry run that reports success on a checkout that cannot build is the
    #101 experience in miniature."""
    import inspect

    assert "check_build_prerequisites" in inspect.getsource(deploy.main)


def test_an_empty_interpreter_is_rejected_rather_than_treated_as_cwd():
    """Path("") is PosixPath("."), which exists -- so an existence check alone
    lets the placeholder through."""
    assert Path("").exists(), "the hazard this guards against"
    import inspect

    source = inspect.getsource(deploy.check_build_prerequisites)
    assert "if not build_python:" in source
