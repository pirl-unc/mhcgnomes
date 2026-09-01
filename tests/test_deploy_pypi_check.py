"""
Whether `deploy.py` checks that the release it just tagged actually shipped.

The script used to end with

    ok(f"Release tag pushed: {tag}")
    note("GitHub Actions will build and publish this tag to PyPI.")

and that second line has been false since #83: the workflow's
trusted-publisher exchange fails with `invalid-publisher`, so the tag lands on
GitHub and nothing reaches PyPI. The script reported success either way, which
is how "done means merged AND deployed" ends up satisfied by a sentence.

The check has to distinguish three outcomes, not two. A network failure is not
evidence that a release is missing, and treating it as one would make deploys
fail on flaky wifi.

https://github.com/pirl-unc/mhcgnomes/issues/83
"""

import io
import json
import urllib.error
from pathlib import Path

import pytest

deploy = pytest.importorskip("deploy")


def _config(tmp_path, **overrides):
    values = {
        "version_file": Path("mhcgnomes/version.py"),
        "required_branch": "main",
        "remote": "origin",
        "dry_run": False,
        "fetch": False,
        "env": None,
        "python": "python3",
        "build_env": None,
        "pypi_project": "mhcgnomes",
        "pypi_timeout": 0.0,
        "check_pypi": True,
    }
    values.update(overrides)
    return deploy.Config(**values)


def _fake_urlopen(payload=None, error=None):
    def opener(url, timeout=None):
        if error is not None:
            raise error
        return io.BytesIO(json.dumps(payload).encode())

    class _Ctx:
        def __init__(self, url, timeout=None):
            self.stream = opener(url, timeout)

        def __enter__(self):
            return self.stream

        def __exit__(self, *exc):
            return False

    return _Ctx


# ---------------------------------------------------------------------------
# The lookup itself
# ---------------------------------------------------------------------------


def test_versions_are_read_from_the_releases_map(monkeypatch):
    monkeypatch.setattr(
        deploy.urllib.request,
        "urlopen",
        _fake_urlopen({"releases": {"1.0.0": [], "1.1.0": []}}),
    )
    assert deploy.pypi_released_versions("mhcgnomes") == {"1.0.0", "1.1.0"}


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.URLError("no route to host"),
        TimeoutError("timed out"),
        OSError("connection reset"),
    ],
)
def test_an_unreachable_index_is_none_not_empty(monkeypatch, error):
    """
    The distinction the whole check rests on. Returning an empty set here would
    make every offline deploy report the release as missing.
    """
    monkeypatch.setattr(deploy.urllib.request, "urlopen", _fake_urlopen(error=error))
    assert deploy.pypi_released_versions("mhcgnomes") is None


def test_a_payload_without_releases_is_none(monkeypatch):
    monkeypatch.setattr(deploy.urllib.request, "urlopen", _fake_urlopen({"info": {}}))
    assert deploy.pypi_released_versions("mhcgnomes") is None


# ---------------------------------------------------------------------------
# The three outcomes
# ---------------------------------------------------------------------------


def test_a_published_version_is_present(monkeypatch, tmp_path):
    monkeypatch.setattr(deploy, "pypi_released_versions", lambda project, **kw: {"3.54.0"})
    assert deploy.await_pypi_publication(_config(tmp_path), "3.54.0") == deploy.PYPI_PRESENT


def test_a_reachable_index_without_the_version_is_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(deploy, "pypi_released_versions", lambda project, **kw: {"3.53.0"})
    assert deploy.await_pypi_publication(_config(tmp_path), "3.54.0") == deploy.PYPI_ABSENT


def test_an_unreachable_index_is_unknown(monkeypatch, tmp_path):
    monkeypatch.setattr(deploy, "pypi_released_versions", lambda project, **kw: None)
    assert deploy.await_pypi_publication(_config(tmp_path), "3.54.0") == deploy.PYPI_UNKNOWN


# ---------------------------------------------------------------------------
# What the operator is told, and what the shell sees
# ---------------------------------------------------------------------------


def test_present_exits_zero(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(deploy, "await_pypi_publication", lambda cfg, v: deploy.PYPI_PRESENT)
    code = deploy.report_pypi_outcome(_config(tmp_path), "3.54.0", "v3.54.0", cwd=tmp_path)
    assert code == 0
    # note()/ok() write to stderr, which is what makes them survive a caller
    # that is capturing stdout.
    assert "is on PyPI" in capsys.readouterr().err


def test_unknown_exits_zero_but_does_not_claim_success(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(deploy, "await_pypi_publication", lambda cfg, v: deploy.PYPI_UNKNOWN)
    code = deploy.report_pypi_outcome(_config(tmp_path), "3.54.0", "v3.54.0", cwd=tmp_path)
    assert code == 0
    err = capsys.readouterr().err
    assert "Could not reach PyPI" in err
    assert "is on PyPI" not in err


def test_absent_exits_three_and_says_what_to_do(monkeypatch, tmp_path, capsys):
    """
    Exit 3 rather than 1 so a caller can tell "the release did not land" from
    "the script could not run", and the message must not say to re-run
    deploy.sh: the tag exists by now, so that stops on the existing tag (#152).
    """
    monkeypatch.setattr(deploy, "await_pypi_publication", lambda cfg, v: deploy.PYPI_ABSENT)
    dist = tmp_path / "dist"
    dist.mkdir()
    wheel = dist / "mhcgnomes-3.54.0-py3-none-any.whl"
    sdist = dist / "mhcgnomes-3.54.0.tar.gz"
    wheel.write_text("")
    sdist.write_text("")

    code = deploy.report_pypi_outcome(_config(tmp_path), "3.54.0", "v3.54.0", cwd=tmp_path)
    assert code == 3
    err = capsys.readouterr().err
    assert "no 3.54.0" in err
    assert "#83" in err
    assert "Do NOT re-run deploy.sh" in err
    assert "twine upload" in err
    assert str(wheel) in err and str(sdist) in err


def test_absent_with_no_artifacts_says_so(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(deploy, "await_pypi_publication", lambda cfg, v: deploy.PYPI_ABSENT)
    code = deploy.report_pypi_outcome(_config(tmp_path), "3.54.0", "v3.54.0", cwd=tmp_path)
    assert code == 3
    assert "No dist/ artifacts" in capsys.readouterr().err


def test_the_check_can_be_skipped_without_touching_the_network(monkeypatch, tmp_path, capsys):
    def explode(*args, **kwargs):
        raise AssertionError("--skip-pypi-check must not look anything up")

    monkeypatch.setattr(deploy, "await_pypi_publication", explode)
    code = deploy.report_pypi_outcome(
        _config(tmp_path, check_pypi=False), "3.54.0", "v3.54.0", cwd=tmp_path
    )
    assert code == 0
    err = capsys.readouterr().err
    assert "Skipping the PyPI check" in err
    assert "Nothing has confirmed" in err


def test_the_flags_are_wired_through():
    cfg = deploy.parse_args(
        ["--skip-pypi-check", "--pypi-timeout", "12", "--pypi-project", "other"]
    )
    assert cfg.check_pypi is False
    assert cfg.pypi_timeout == 12.0
    assert cfg.pypi_project == "other"
    assert deploy.parse_args([]).check_pypi is True
