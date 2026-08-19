import argparse
import json
import sys
from collections.abc import Sequence
from typing import Optional

from .errors import ParseError
from .function_api import parse
from .version import __version__

COLUMN_NAMES = (
    "input",
    "type",
    "normalized",
    "compact",
    "species",
    "gene",
    "mhc_class",
    "properties",
)


def _stringify(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return ",".join(_stringify(x) for x in value)
    if isinstance(value, dict):
        return ",".join(f"{k}:{_stringify(v)}" for k, v in value.items())
    return str(value)


def _record_to_properties(record) -> str:
    if not record:
        return ""
    if not isinstance(record, dict):
        return _stringify(record)
    return "; ".join(f"{k}={_stringify(v)}" for k, v in record.items())


def _build_result_row(raw_input: str, result) -> dict[str, str]:
    type_name = type(result).__name__
    try:
        record = result.to_record()
    except NotImplementedError:
        record = {}
    return {
        "input": raw_input,
        "type": type_name,
        "normalized": result.to_string(),
        "compact": result.compact_string(),
        "species": _stringify(getattr(result, "species_prefix", "")),
        "gene": _stringify(getattr(result, "gene_name", "")),
        "mhc_class": _stringify(getattr(result, "mhc_class", "")),
        "properties": _record_to_properties(record),
    }


def _build_error_row(raw_input: str, message: str) -> dict[str, str]:
    return {
        "input": raw_input,
        "type": "ParseError",
        "normalized": "",
        "compact": "",
        "species": "",
        "gene": "",
        "mhc_class": "",
        "properties": message,
    }


def _sanitize_cell(value: str) -> str:
    return value.replace("\t", " ").replace("\n", " ").strip()


def _render_tsv(rows: Sequence[dict[str, str]], include_header: bool) -> str:
    lines = []
    if include_header:
        lines.append("\t".join(COLUMN_NAMES))
    for row in rows:
        lines.append("\t".join(_sanitize_cell(row[column]) for column in COLUMN_NAMES))
    return "\n".join(lines)


def _render_table(rows: Sequence[dict[str, str]], include_header: bool) -> str:
    widths = {column: len(column) for column in COLUMN_NAMES}
    for row in rows:
        for column in COLUMN_NAMES:
            widths[column] = max(widths[column], len(_sanitize_cell(row[column])))

    lines = []
    if include_header:
        header = " | ".join(column.ljust(widths[column]) for column in COLUMN_NAMES)
        divider = "-+-".join("-" * widths[column] for column in COLUMN_NAMES)
        lines.extend([header, divider])

    for row in rows:
        row_text = " | ".join(
            _sanitize_cell(row[column]).ljust(widths[column]) for column in COLUMN_NAMES
        )
        lines.append(row_text)
    return "\n".join(lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mhcgnomes",
        description="Parse MHC strings and print a table with parsed properties.",
        epilog="Manage pinned external data with 'mhcgnomes data'.",
    )
    parser.add_argument(
        "names",
        nargs="*",
        help="MHC names to parse. If omitted, non-empty lines are read from stdin.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--default-species",
        default="HLA",
        help="Default species prefix used when the input is missing one (default: HLA).",
    )
    parser.add_argument(
        "--infer-class2-pairing",
        action="store_true",
        help="Infer canonical Class II alpha chain when only beta chain is given.",
    )
    parser.add_argument(
        "--max-allele-fields",
        type=int,
        default=None,
        help="If set, restrict parsed alleles to this many fields.",
    )
    parser.add_argument(
        "--format",
        choices=("table", "tsv", "json"),
        default="table",
        help="Output format (default: table).",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Omit header row in table/tsv output.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 on the first parse error.",
    )
    return parser


def _collect_names(positional_names: Sequence[str]) -> list[str]:
    if positional_names:
        return [name for name in positional_names if name and name.strip()]
    if sys.stdin.isatty():
        return []
    return [line.strip() for line in sys.stdin if line.strip()]


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]
    if argv and argv[0] == "data":
        from .external_data import main as external_data_main

        return external_data_main(argv[1:])

    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    names = _collect_names(args.names)
    if not names:
        parser.error("Provide one or more names as arguments or via stdin.")

    rows = []
    for name in names:
        try:
            result = parse(
                name,
                default_species=args.default_species,
                infer_class2_pairing=args.infer_class2_pairing,
                max_allele_fields=args.max_allele_fields,
                raise_on_error=args.strict,
            )
        except ParseError as err:
            print(f"ParseError: {err}", file=sys.stderr)
            return 1

        if result is None:
            message = f"Could not parse '{name}'"
            if args.strict:
                print(f"ParseError: {message}", file=sys.stderr)
                return 1
            rows.append(_build_error_row(name, message))
        else:
            rows.append(_build_result_row(name, result))

    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return 0
    if args.format == "tsv":
        print(_render_tsv(rows, include_header=not args.no_header))
        return 0

    print(_render_table(rows, include_header=not args.no_header))
    return 0
