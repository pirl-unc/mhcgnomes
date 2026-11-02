import argparse

from mhcgnomes.validate_external_names import (
    DEFAULT_FASTA_PATHS,
    add_validation_arguments,
    fasta_names,
    main,
    run_validation,
    validate_fasta,
)


def test_fasta_names_reads_provider_header_name_field():
    lines = [
        ">HLA:HLA00001 A*01:01:01:01 365 bp\n",
        "AAAA\n",
        ">IPD-MHC:DLA04814 DLA-DQA1*012:01:2 77 bp\n",
    ]
    assert list(fasta_names(lines)) == [(1, "A*01:01:01:01"), (3, "DLA-DQA1*012:01:2")]


def test_validate_fasta_checks_human_and_cross_species_names(tmp_path):
    path = tmp_path / "protein.fasta"
    path.write_text(
        ">HLA:HLA00001 A*01:01:01:01 365 bp\n"
        "AAAA\n"
        ">IPD-MHC:DLA04814 DLA-DQA1*012:01:2 77 bp\n"
        "AAAA\n"
        ">IPD-MHC:FISH08119 Onmy-DAA*01:01 74 bp\n"
        "AAAA\n"
        ">IPD-MHC:SLA05920 SLA-DMA*01:01:01 92 bp\n"
        "AAAA\n",
        encoding="utf-8",
    )

    result = validate_fasta(path)

    assert result.record_count == 4
    assert result.unique_name_count == 4
    assert result.failures == ()


def test_validate_fasta_reports_malformed_and_unparseable_headers(tmp_path):
    path = tmp_path / "bad.fasta"
    path.write_text(">missing-name\nAAAA\n>DB not-an-allele\nAAAA\n", encoding="utf-8")

    result = validate_fasta(path)

    assert result.record_count == 2
    assert result.unique_name_count == 1
    assert len(result.failures) == 2
    assert "malformed FASTA header" in result.failures[0]
    assert "not-an-allele" in result.failures[1]


def test_validate_fasta_rejects_file_without_headers(tmp_path):
    path = tmp_path / "empty.fasta"
    path.write_text("AAAA\n", encoding="utf-8")

    result = validate_fasta(path)

    assert result.failures == ("no FASTA headers found",)


def test_cli_reports_missing_source(tmp_path, capsys):
    missing = tmp_path / "missing.fasta"

    assert main([str(missing)]) == 1
    assert "mhcgnomes data download --group validation" in capsys.readouterr().err


def test_add_validation_arguments_defaults_to_validation_group_files():
    parser = argparse.ArgumentParser()
    add_validation_arguments(parser)

    args = parser.parse_args([])

    assert tuple(args.paths) == DEFAULT_FASTA_PATHS
    assert args.max_failures == 20


def test_run_validation_limits_printed_failures(tmp_path, capsys):
    path = tmp_path / "bad.fasta"
    path.write_text(
        ">DB not-an-allele-one\nAAAA\n>DB not-an-allele-two\nAAAA\n",
        encoding="utf-8",
    )

    assert run_validation([path], max_failures=1) == 1
    captured = capsys.readouterr()
    assert "parsed 2 unique allele names from 2 FASTA records" in captured.out
    assert "2 names failed" in captured.err
    assert "not-an-allele-one" in captured.err
    assert "not-an-allele-two" not in captured.err


def test_run_validation_passes_clean_file(tmp_path, capsys):
    path = tmp_path / "good.fasta"
    path.write_text(">HLA:HLA00001 A*01:01:01:01 365 bp\nAAAA\n", encoding="utf-8")

    assert run_validation([path], max_failures=20) == 0
    assert capsys.readouterr().err == ""
