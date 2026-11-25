# PYTHON_ARGCOMPLETE_OK
"""Command-line interface for parsing MHC nomenclature strings and managing external data."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from collections.abc import Mapping, Sequence
from typing import Any

import argcomplete

from .cli_help import HelpArgumentParser, style_table_header
from .version import __version__

COLUMN_NAMES = (
    "input",
    "type",
    "normalized",
    "compact",
    "species",
    "gene_name",
    "mhc_class",
    "properties",
)

RESULT_TYPE_NAMES = (
    "AccessionedAllele",
    "Allele",
    "AlleleWithoutGene",
    "AmbiguousAlleles",
    "Class2Locus",
    "Gene",
    "Haplotype",
    "MhcClass",
    "Pair",
    "Serotype",
    "Species",
    "Supertype",
)


def load_result_types() -> dict[str, type]:
    """Import and return the mapping from public result class names to classes."""
    from .accessioned_allele import AccessionedAllele
    from .allele import Allele
    from .allele_without_gene import AlleleWithoutGene
    from .ambiguous_alleles import AmbiguousAlleles
    from .class2_locus import Class2Locus
    from .gene import Gene
    from .haplotype import Haplotype
    from .mhc_class import MhcClass
    from .pair import Pair
    from .serotype import Serotype
    from .species import Species
    from .supertype import Supertype

    return {
        cls.__name__: cls
        for cls in (
            AccessionedAllele,
            Allele,
            AlleleWithoutGene,
            AmbiguousAlleles,
            Class2Locus,
            Gene,
            Haplotype,
            MhcClass,
            Pair,
            Serotype,
            Species,
            Supertype,
        )
    }


def outcome_to_cli_row(raw_input, outcome):
    """Project a public parse-outcome row into the CLI's string columns.

    Accepts the same outcomes as parse_outcome_to_row. Uses the shared
    ``gene_name`` column directly (short gene name), leaving full ``gene``
    identifiers in ``properties`` / ``to_record()``. Missing scalar display
    values become empty strings. Unsupported outcomes/serialization errors
    propagate.
    """
    from .parse_outcome import parse_outcome_to_row

    row = parse_outcome_to_row(raw_input, outcome)
    return {column: "" if row.get(column) is None else str(row[column]) for column in COLUMN_NAMES}


def parse_result_type_names(value: str) -> tuple[str, ...]:
    """Validate comma-separated public result class names without importing result classes."""
    names = [name.strip() for name in value.split(",")]
    unknown = [name for name in names if name not in RESULT_TYPE_NAMES]
    if unknown:
        raise argparse.ArgumentTypeError(
            f"Unknown result type(s): {', '.join(repr(name) for name in unknown)}; "
            f"choose from {', '.join(sorted(RESULT_TYPE_NAMES))}"
        )
    return tuple(dict.fromkeys(names))


def resolve_result_types(names: Sequence[str] | None) -> tuple[type, ...] | None:
    """Resolve validated result class names to their runtime classes."""
    if names is None:
        return None
    result_types = load_result_types()
    return tuple(result_types[name] for name in names)


def complete_result_type_names(prefix: str, **kwargs: Any) -> list[str]:
    """Complete comma-separated result class names locally for ``--result-types``."""
    head, sep, tail = prefix.rpartition(",")
    chosen = {part.strip() for part in head.split(",") if part.strip()} if sep else set()
    base = f"{head}," if sep else ""
    return [
        f"{base}{name}"
        for name in RESULT_TYPE_NAMES
        if name not in chosen and name.startswith(tail)
    ]


def complete_top_level_names(
    prefix: str, parsed_args: argparse.Namespace, **kwargs: Any
) -> list[str]:
    """Suggest the ``data`` subcommand for the first positional token."""
    if not getattr(parsed_args, "names", None) and "data".startswith(prefix):
        return ["data"]
    return []


def sanitize_cell(value: str) -> str:
    """Collapse embedded tabs and newlines in a single table or TSV cell."""
    return value.replace("\t", " ").replace("\n", " ").strip()


def render_tsv(rows: Sequence[dict[str, str]], include_header: bool) -> str:
    """Format parsed CLI rows as tab-separated values."""
    lines = []
    if include_header:
        lines.append("\t".join(COLUMN_NAMES))
    for row in rows:
        lines.append("\t".join(sanitize_cell(row[column]) for column in COLUMN_NAMES))
    return "\n".join(lines)


def render_table(
    rows: Sequence[dict[str, str]],
    include_header: bool,
    stream: Any = None,
) -> str:
    """Format parsed CLI rows as an aligned plain-text table with optional TTY header color."""
    widths = {column: len(column) for column in COLUMN_NAMES}
    for row in rows:
        for column in COLUMN_NAMES:
            widths[column] = max(widths[column], len(sanitize_cell(row[column])))

    lines = []
    if include_header:
        header = " | ".join(column.ljust(widths[column]) for column in COLUMN_NAMES)
        divider = "-+-".join("-" * widths[column] for column in COLUMN_NAMES)
        lines.extend([style_table_header(header, stream), divider])

    for row in rows:
        row_text = " | ".join(
            sanitize_cell(row[column]).ljust(widths[column]) for column in COLUMN_NAMES
        )
        lines.append(row_text)
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the top-level ``mhcgnomes`` argument parser without heavy imports."""
    parser = HelpArgumentParser(
        prog="mhcgnomes",
        description="Parse MHC strings and print a table with parsed properties.",
        epilog="Manage pinned external data with 'mhcgnomes data'.",
    )
    names_arg = parser.add_argument(
        "names",
        nargs="*",
        help="MHC names to parse. If omitted, non-empty lines are read from stdin.",
    )
    names_arg.completer = complete_top_level_names  # type: ignore[attr-defined]
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    species_options = parser.add_mutually_exclusive_group()
    species_options.add_argument(
        "--default-species",
        default="HLA",
        help="Default species prefix used when the input is missing one (default: HLA).",
    )
    species_options.add_argument(
        "--species",
        help="Require exactly this species, using the Python species= policy.",
    )
    parser.add_argument(
        "--use-allele-aliases",
        action="store_true",
        help="Resolve supported historical allele names.",
    )
    parser.add_argument(
        "--require-explicit-species",
        action="store_true",
        help="Reject names whose species was inferred or defaulted.",
    )
    result_types_arg = parser.add_argument(
        "--result-types",
        type=parse_result_type_names,
        metavar="Allele,Gene,Pair",
        help="Only accept these comma-separated result class names.",
    )
    result_types_arg.completer = complete_result_type_names  # type: ignore[attr-defined]
    parser.add_argument(
        "--class",
        dest="mhc_class",
        choices=("I", "II"),
        help="Only accept results in this MHC class.",
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


def build_data_completion_parser() -> argparse.ArgumentParser:
    """Build a lightweight completion parser for ``mhcgnomes data ...`` subcommands."""
    from .external_data import attach_data_subparsers

    parser = HelpArgumentParser(prog="mhcgnomes")
    subparsers = parser.add_subparsers(dest="command")
    data_parser = subparsers.add_parser(
        "data",
        help="List, download, or validate checksum-pinned IMGT/IPD inputs.",
    )
    attach_data_subparsers(data_parser)
    return parser


def is_completing_data_subcommand(environ: Mapping[str, str] | None = None) -> bool:
    """Return True when argcomplete is completing arguments under ``mhcgnomes data``."""
    env = os.environ if environ is None else environ
    comp_line = env.get("COMP_LINE", "")
    if not comp_line:
        return False
    raw_point = env.get("COMP_POINT")
    try:
        comp_point = int(raw_point) if raw_point is not None else len(comp_line)
    except ValueError:
        comp_point = len(comp_line)
    before_cursor = comp_line[:comp_point]
    try:
        tokens = shlex.split(before_cursor)
    except ValueError:
        tokens = before_cursor.split()
    if len(tokens) < 2 or tokens[1] != "data":
        return False
    return len(tokens) > 2 or before_cursor[-1:].isspace()


def collect_names(positional_names: Sequence[str]) -> list[str]:
    """Collect non-empty MHC names from CLI positional arguments or piped stdin."""
    if positional_names:
        return [name for name in positional_names if name and name.strip()]
    if sys.stdin.isatty():
        return []
    return [line.strip() for line in sys.stdin if line.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``mhcgnomes`` command-line interface."""
    if argv is None and "_ARGCOMPLETE" in os.environ:
        completion_parser = (
            build_data_completion_parser()
            if is_completing_data_subcommand()
            else build_arg_parser()
        )
        argcomplete.autocomplete(completion_parser)

    argv_list = list(argv) if argv is not None else sys.argv[1:]
    if argv_list and argv_list[0] == "data":
        from .external_data import main as external_data_main

        return external_data_main(argv_list[1:])

    parser = build_arg_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv_list)

    names = collect_names(args.names)
    if not names:
        parser.error("Provide one or more names as arguments or via stdin.")

    from .errors import ParseError
    from .function_api import parse

    required_result_types = resolve_result_types(args.result_types)

    rows = []
    for name in names:
        try:
            result = parse(
                name,
                default_species=args.default_species,
                species=args.species,
                use_allele_aliases=args.use_allele_aliases,
                require_explicit_species=args.require_explicit_species,
                required_result_types=required_result_types,
                only_class1=args.mhc_class == "I",
                only_class2=args.mhc_class == "II",
                infer_class2_pairing=args.infer_class2_pairing,
                max_allele_fields=args.max_allele_fields,
                raise_on_error=True,
            )
        except ParseError as err:
            if args.strict:
                print(f"ParseError: {err}", file=sys.stderr)
                return 1
            rows.append(outcome_to_cli_row(name, err))
            continue

        if result is None:
            message = f"Could not parse '{name}'"
            if args.strict:
                print(f"ParseError: {message}", file=sys.stderr)
                return 1
            rows.append(outcome_to_cli_row(name, ParseError(message)))
        else:
            rows.append(outcome_to_cli_row(name, result))

    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return 0
    if args.format == "tsv":
        print(render_tsv(rows, include_header=not args.no_header))
        return 0

    print(render_table(rows, include_header=not args.no_header, stream=sys.stdout))
    return 0


def __getattr__(name: str) -> Any:
    if name == "RESULT_TYPES":
        value = load_result_types()
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
