import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "mhcgnomes", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "mhcgnomes" in result.stdout.lower()


def test_cli_table_output_for_valid_allele():
    result = run_cli("HLA-A*02:01")
    assert result.returncode == 0
    output = result.stdout
    assert "input" in output
    assert "type" in output
    assert "normalized" in output
    assert "properties" in output
    assert "HLA-A*02:01" in output
    assert "Allele" in output


def test_cli_tsv_output_multiple_inputs():
    result = run_cli("--format", "tsv", "HLA-A*02:01", "DQ2.5")
    assert result.returncode == 0
    lines = [line for line in result.stdout.strip().splitlines() if line]
    assert len(lines) == 3
    assert lines[0].split("\t") == [
        "input",
        "type",
        "normalized",
        "compact",
        "species",
        "gene",
        "mhc_class",
        "properties",
    ]
    assert "HLA-A*02:01" in lines[1]
    assert "DQ2.5" in lines[2]


def test_cli_strict_mode_fails_on_unparseable_input():
    result = run_cli("--strict", "NOT_A_REAL_ALLELE")
    assert result.returncode == 1
    assert "ParseError" in result.stderr


def test_cli_non_strict_shows_parse_error_row():
    result = run_cli("--format", "tsv", "NOT_A_REAL_ALLELE")
    assert result.returncode == 0
    assert "ParseError" in result.stdout
