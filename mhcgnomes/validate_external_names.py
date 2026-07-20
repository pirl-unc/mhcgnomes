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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse every allele name in cached official IMGT/IPD protein FASTA files."
    )
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_FASTA_PATHS)
    parser.add_argument("--max-failures", type=int, default=20)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    failed = False
    for path in args.paths:
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
            for failure in result.failures[: args.max_failures]:
                print(f"  {failure}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
