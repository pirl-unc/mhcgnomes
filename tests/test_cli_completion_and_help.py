"""CLI lazy startup, argcomplete tab completion, help styling, and tooling pins (#237, #259, #264)."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from mhcgnomes.cli_help import (
    HelpArgumentParser,
    color_enabled,
    style_help,
    style_status,
    style_table_header,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HEAVY_MODULES = ("pandas", "numpy", "yaml")


def build_subprocess_env(**extra: str) -> dict[str, str]:
    """Build a subprocess environment with this checkout first on PYTHONPATH."""
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{existing}" if existing else str(REPO_ROOT)
    env.update(extra)
    return env


@pytest.mark.parametrize(
    "module_name",
    [
        "mhcgnomes",
        "mhcgnomes.cli",
        "mhcgnomes.cli_help",
        "mhcgnomes.data",
        "mhcgnomes.external_data",
        "mhcgnomes.validate_external_names",
    ],
)
def test_cli_and_package_import_avoid_heavy_dependencies(module_name):
    code = (
        "import importlib, sys\n"
        f"importlib.import_module({module_name!r})\n"
        f"loaded = [m for m in {HEAVY_MODULES!r} if m in sys.modules]\n"
        "assert not loaded, f'Heavy modules loaded on import: {loaded}'\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        env=build_subprocess_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "comp_line,expected_items",
    [
        ("mhcgnomes --for", {"--format"}),
        ("mhcgnomes --format ", {"table", "tsv", "json"}),
        ("mhcgnomes --class ", {"I", "II"}),
        ("mhcgnomes --result-types Al", {"Allele", "AlleleWithoutGene"}),
        ("mhcgnomes --result-types Allele,P", {"Allele,Pair"}),
        ("mhcgnomes da", {"data"}),
        ("mhcgnomes data ", {"list", "download", "validate"}),
        ("mhcgnomes data download --off", {"--offline"}),
        ("mhcgnomes data list --group val", {"validation"}),
        ("mhcgnomes data validate --max", {"--max-failures"}),
    ],
)
def test_argcomplete_returns_expected_completions_without_heavy_imports(
    tmp_path, comp_line, expected_items
):
    out_file = tmp_path / "argcomplete_out.txt"
    env = build_subprocess_env(
        _ARGCOMPLETE="1",
        _ARGCOMPLETE_IFS="\n",
        _ARGCOMPLETE_STDOUT_FILENAME=str(out_file),
        COMP_LINE=comp_line,
        COMP_POINT=str(len(comp_line)),
    )
    code = (
        "import sys\n"
        "from mhcgnomes import cli\n"
        "try:\n"
        "    cli.main()\n"
        "except SystemExit as exc:\n"
        f"    loaded = [m for m in {HEAVY_MODULES!r} if m in sys.modules]\n"
        "    assert not loaded, f'Heavy modules loaded during completion: {loaded}'\n"
        "    raise SystemExit(exc.code)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    completions = {
        line.strip() for line in out_file.read_text(encoding="utf-8").splitlines() if line.strip()
    }
    assert expected_items <= completions, f"Expected {expected_items} in completions {completions}"


def test_entry_modules_have_argcomplete_marker_within_first_1024_bytes():
    for rel in (
        "mhcgnomes/cli.py",
        "mhcgnomes/__main__.py",
        "mhcgnomes/external_data.py",
    ):
        head = (REPO_ROOT / rel).read_bytes()[:1024]
        assert b"PYTHON_ARGCOMPLETE_OK" in head, f"Missing marker in {rel}"


def test_help_styling_plain_in_format_help_and_cyan_only_on_tty(monkeypatch):
    class FakeTTY(io.StringIO):
        def isatty(self):
            return True

    parser = HelpArgumentParser(prog="mhcgnomes-test", description="Test CLI")
    parser.add_argument("--species", help="Require ``species`` match")
    plain = parser.format_help()
    assert "\033[" not in plain
    assert "``" not in plain

    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm-256color")

    non_tty = io.StringIO()
    assert not color_enabled(non_tty)
    parser.print_help(file=non_tty)
    assert "\033[" not in non_tty.getvalue()

    tty = FakeTTY()
    assert color_enabled(tty)
    parser.print_help(file=tty)
    styled = tty.getvalue()
    assert "\033[1musage:\033[0m" in styled
    assert "\033[36m--species\033[0m" in styled
    assert "\033[1;36m" in styled
    assert style_table_header("input | type\nHLA-A | Gene\n", tty).startswith("\033[1;36m")
    assert style_status("missing", tty, dim=True) == "\033[2mmissing\033[0m"
    assert style_status("invalid", tty, warning=True) == "\033[33minvalid\033[0m"
    assert style_status("downloaded", tty) == "downloaded"

    monkeypatch.setenv("NO_COLOR", "1")
    assert not color_enabled(tty)
    assert "\033[" not in style_help(plain, tty)

    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "dumb")
    assert not color_enabled(tty)


def test_pyproject_ships_only_mhcgnomes_console_script():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]
    assert scripts == {"mhcgnomes": "mhcgnomes.cli:main"}


def test_ruff_pin_matches_between_pyproject_and_pre_commit():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dev_deps = pyproject["project"]["optional-dependencies"]["dev"]
    ruff_pins = [dep for dep in dev_deps if dep.startswith("ruff==")]
    assert len(ruff_pins) == 1, f"Expected explicit ruff==X.Y.Z pin in dev deps, got {dev_deps}"
    pinned_version = ruff_pins[0].split("==", 1)[1]

    pre_commit = yaml.safe_load((REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    ruff_repos = [
        repo
        for repo in pre_commit["repos"]
        if repo.get("repo") == "https://github.com/astral-sh/ruff-pre-commit"
    ]
    assert len(ruff_repos) == 1
    assert ruff_repos[0]["rev"] == f"v{pinned_version}"
