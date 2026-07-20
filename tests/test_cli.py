import hashlib
import json
import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "mhcgnomes", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def run_cli_with_stdin(stdin_text, *args):
    return subprocess.run(
        [sys.executable, "-m", "mhcgnomes", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "mhcgnomes" in result.stdout.lower()
    assert "mhcgnomes data" in result.stdout


def test_data_command_lists_sources_by_default():
    result = run_cli("data")

    assert result.returncode == 0
    assert "imgt-hla-allele-history-3.42.0" in result.stdout
    assert "ipd-mhc-3.8.0.0-protein" in result.stdout


def test_data_list_is_explicit_alias_for_default_action():
    default = run_cli("data")
    explicit = run_cli("data", "list")

    assert explicit.returncode == 0
    assert explicit.stdout == default.stdout


def test_data_download_help_owns_download_options():
    result = run_cli("data", "download", "--help")

    assert result.returncode == 0
    assert "--cache-dir" in result.stdout
    assert "--destination" in result.stdout
    assert "--mirror" in result.stdout
    assert "--offline" in result.stdout


def test_data_download_options_are_not_accepted_by_data_group():
    result = run_cli("data", "--offline")

    assert result.returncode == 2
    assert "unrecognized arguments: --offline" in result.stderr


def test_data_download_materializes_from_local_mirror_offline(tmp_path):
    payload = b"nested CLI payload"
    digest = hashlib.sha256(payload).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "nested-cli-source",
                        "filename": "nested.dat",
                        "provider": "Example",
                        "release": "1",
                        "url": "https://official.example/nested.dat",
                        "sha256": digest,
                        "license_url": "https://official.example/license",
                        "groups": ["example"],
                        "default": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / "nested.dat").write_bytes(payload)
    destination = tmp_path / "destination"

    result = run_cli(
        "data",
        "download",
        "--manifest",
        str(manifest),
        "--cache-dir",
        str(tmp_path / "cache"),
        "--destination",
        str(destination),
        "--mirror",
        str(mirror),
        "--offline",
    )

    assert result.returncode == 0
    assert (destination / "nested.dat").read_bytes() == payload
    assert "nested-cli-source" in result.stdout


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


def test_cli_reads_names_from_stdin_when_no_positional_args_are_given():
    result = run_cli_with_stdin("HLA-A*02:01\nDQ2.5\n", "--format", "json")

    assert result.returncode == 0
    rows = json.loads(result.stdout)
    assert [row["input"] for row in rows] == ["HLA-A*02:01", "DQ2.5"]
    assert rows[0]["normalized"] == "HLA-A*02:01"
    assert rows[1]["type"] == "Pair"


def test_cli_no_header_omits_tsv_header_row():
    result = run_cli("--format", "tsv", "--no-header", "HLA-A*02:01")

    assert result.returncode == 0
    lines = [line for line in result.stdout.strip().splitlines() if line]
    assert len(lines) == 1
    assert not lines[0].startswith("input\t")
    assert lines[0].startswith("HLA-A*02:01\tAllele\t")


def test_cli_errors_when_no_input_is_provided():
    result = run_cli_with_stdin("")

    assert result.returncode == 2
    assert "Provide one or more names" in result.stderr
