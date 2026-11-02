#!/usr/bin/env python3
"""Validate every allele name in cached official IMGT/IPD protein FASTA files."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from mhcgnomes import Allele, parse

DEFAULT_FASTA_PATHS = (
    Path(".external-data/hla_prot.fasta"),
    Path(".external-data/MHC_prot.fasta"),
)


@dataclass(frozen=True)
class ValidationResult:
    path: Path
    record_count: int
    unique_name_count: int
    failures: tuple[str, ...]


def fasta_names(lines: Iterable[str]) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(lines, start=1):
        if not line.startswith(">"):
            continue
        fields = line[1:].split()
        if len(fields) < 2:
            yield line_number, ""
        else:
            yield line_number, fields[1]


def validate_fasta(path: Path) -> ValidationResult:
    failures = []
    names = set()
    record_count = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, name in fasta_names(handle):
            record_count += 1
            if not name:
                failures.append(f"line {line_number}: malformed FASTA header")
                continue
            names.add(name)
            try:
                result = parse(name, raise_on_error=False)
            except Exception as exc:  # report the complete upstream compatibility result
                failures.append(f"line {line_number}: {name!r} raised {exc!r}")
                continue
            if not isinstance(result, Allele):
                failures.append(f"line {line_number}: {name!r} parsed as {result!r}")
    if record_count == 0:
        failures.append("no FASTA headers found")
    return ValidationResult(path, record_count, len(names), tuple(failures))


DESCRIPTION = "Parse every allele name in cached official IMGT/IPD protein FASTA files."


def add_validation_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Attach the FASTA paths and failure-limit options to a parser.

    Shared by the standalone ``mhcgnomes-validate-data`` command and by
    ``mhcgnomes data validate`` so both accept the same arguments.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        Parser or subparser to extend. Parsed arguments gain ``paths`` (list
        of Path) and ``max_failures`` (int).

    Returns
    -------
    None
    """
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=DEFAULT_FASTA_PATHS,
        help=(
            "Protein FASTA files to check (default: .external-data/hla_prot.fasta and "
            ".external-data/MHC_prot.fasta, the 'validation' download group)"
        ),
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=20,
        help="Print at most this many failing names per file (default: 20)",
    )


def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser for the standalone ``mhcgnomes-validate-data`` command.

    Returns
    -------
    argparse.ArgumentParser
        Parser accepting the arguments described in add_validation_arguments.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    add_validation_arguments(parser)
    return parser


def run_validation(paths: Sequence[Path], max_failures: int) -> int:
    """
    Validate each FASTA file, print a summary per file and return an exit code.

    The per-file summary goes to stdout; missing files and failing names go
    to stderr.

    Parameters
    ----------
    paths : sequence of Path
        Protein FASTA files to check with validate_fasta.
    max_failures : int
        Print at most this many failures for each file.

    Returns
    -------
    int
        0 when every file exists, has at least one FASTA header, and every
        header's name parses as an Allele; otherwise 1.
    """
    failed = False
    for path in paths:
        if not path.is_file():
            print(
                f"ERROR: missing {path}; run 'mhcgnomes data download --group validation' first",
                file=sys.stderr,
            )
            failed = True
            continue
        result = validate_fasta(path)
        print(
            f"{path}: parsed {result.unique_name_count} unique allele names "
            f"from {result.record_count} FASTA records"
        )
        if result.failures:
            failed = True
            print(f"ERROR: {len(result.failures)} names failed:", file=sys.stderr)
            for failure in result.failures[:max_failures]:
                print(f"  {failure}", file=sys.stderr)
    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run ``mhcgnomes-validate-data``; same as ``mhcgnomes data validate``.

    Parameters
    ----------
    argv : sequence of str or None
        Command-line arguments without the program name; None reads sys.argv.

    Returns
    -------
    int
        Exit code from run_validation.
    """
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    return run_validation(args.paths, args.max_failures)


if __name__ == "__main__":
    raise SystemExit(main())
