"""
Which interpreter `deploy.py` runs the build with, and whether it says so.

Issue #101 was not that the wrong interpreter was chosen -- it was that the
script resolved a venv, printed "Using venv: .venv", and then built with
whatever launched it. The obvious fix, always preferring the venv, is worse
here: develop.sh installs only `.[dev,docs]`, which has no `build` and no
`setuptools`, so the venv usually cannot build at all.

https://github.com/pirl-unc/mhcgnomes/issues/101
"""

import sys

import pytest

deploy = pytest.importorskip("deploy")


def _make_venv(tmp_path, name=".venv", interpreter="python", can_build=False):
    """
    A venv whose interpreter is a stub. `can_build=False` makes it fail any
    command, which is what a develop.sh venv does for `import build` -- exit 0
    for everything would make the stub claim it can build.
    """
    bin_dir = tmp_path / name / "bin"
    bin_dir.mkdir(parents=True)
    script = bin_dir / interpreter
    script.write_text(f"#!/bin/sh\nexit {0 if can_build else 1}\n")
    script.chmod(0o755)
    return bin_dir


def test_venv_python_finds_the_interpreter(tmp_path):
    bin_dir = _make_venv(tmp_path)
    assert deploy.venv_python(bin_dir) == bin_dir / "python"


def test_venv_python_accepts_python3_only(tmp_path):
    bin_dir = _make_venv(tmp_path, interpreter="python3")
    assert deploy.venv_python(bin_dir) == bin_dir / "python3"


def test_venv_python_is_none_without_a_venv():
    assert deploy.venv_python(None) is None


def test_interpreter_can_build_is_true_for_an_environment_that_can():
    """The interpreter running this test suite is one, by construction."""
    assert deploy.interpreter_can_build(sys.executable)


def test_interpreter_can_build_is_false_for_a_missing_interpreter(tmp_path):
    assert not deploy.interpreter_can_build(str(tmp_path / "no-such-python"))


def test_interpreter_can_build_requires_setuptools_too():
    """
    `--no-isolation` means pyproject's build backend is not provisioned for us,
    so probing only `build` would pass on an environment that then fails
    inside the build.
    """
    import inspect

    source = inspect.getsource(deploy.interpreter_can_build)
    assert "import build, setuptools" in source


def test_a_venv_that_cannot_build_falls_back_and_says_why(tmp_path):
    """
    The regression this guards against: preferring a venv that has no `build`
    turns a working release into one that aborts after lint and the full test
    suite.
    """
    bin_dir = _make_venv(tmp_path)  # a stub interpreter; it cannot import build
    chosen, reason = deploy.resolve_build_python(bin_dir, env=None)
    assert chosen == (sys.executable or "python3")
    assert "cannot import build" in reason
    assert str(bin_dir / "python") in reason


def test_no_venv_reports_the_launching_interpreter(tmp_path):
    chosen, reason = deploy.resolve_build_python(None, env=None)
    assert chosen == (sys.executable or "python3")
    assert "no project venv" in reason


def test_a_usable_venv_is_preferred(tmp_path):
    bin_dir = _make_venv(tmp_path, can_build=True)
    chosen, reason = deploy.resolve_build_python(bin_dir, env=None)
    assert chosen == str(bin_dir / "python")
    assert reason == "project venv"


def test_deploy_python_is_not_read_directly(monkeypatch):
    """
    deploy.sh launches deploy.py with it -- `PYTHON_BIN="${DEPLOY_PYTHON:-python3}"` --
    so an explicit override already arrives as sys.executable. Reading the
    variable again here would let it outrank a venv while cfg.env still points
    at that venv, which is the mismatch #101 is about.
    """
    import inspect

    source = inspect.getsource(deploy.resolve_build_python)
    assert "DEPLOY_PYTHON" not in source.split('"""')[2]
