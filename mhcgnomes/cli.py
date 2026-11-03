import argparse
import json
import sys
from collections.abc import Sequence
from typing import Optional

from .allele import Allele
from .allele_without_gene import AlleleWithoutGene
from .ambiguous_alleles import AmbiguousAlleles
from .class2_locus import Class2Locus
from .errors import ParseError
from .function_api import parse
from .gene import Gene
from .haplotype import Haplotype
from .mhc_class import MhcClass
from .pair import Pair
from .parse_outcome import parse_outcome_to_row
from .serotype import Serotype
from .species import Species
from .supertype import Supertype
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


def outcome_to_cli_row(raw_input, outcome):
    """Project a public parse-outcome row into the CLI's legacy string columns.

    Accepts the same outcomes as parse_outcome_to_row. CLI 'gene' is the short
    gene_name; the DataFrame's legacy 'gene' column remains a full identifier.
    Record fields are presented in properties. Missing scalar display values
    become empty strings. Unsupported outcomes/serialization errors propagate.
    """
    row = parse_outcome_to_row(raw_input, outcome)
    row["gene"] = row["gene_name"]
    return {column: "" if row.get(column) is None else str(row[column]) for column in COLUMN_NAMES}


RESULT_TYPES = {
    cls.__name__: cls
    for cls in (
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


def _parse_result_types(value):
    names = [name.strip() for name in value.split(",")]
    unknown = [name for name in names if name not in RESULT_TYPES]
    if unknown:
        raise argparse.ArgumentTypeError(
            f"Unknown result type(s): {', '.join(repr(name) for name in unknown)}; "
            f"choose from {', '.join(sorted(RESULT_TYPES))}"
        )
    return tuple(dict.fromkeys(RESULT_TYPES[name] for name in names))


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
    parser.add_argument(
        "--result-types",
        type=_parse_result_types,
        metavar="Allele,Gene,Pair",
        help="Only accept these comma-separated result class names.",
    )
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
                species=args.species,
                use_allele_aliases=args.use_allele_aliases,
                require_explicit_species=args.require_explicit_species,
                required_result_types=args.result_types,
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
        print(_render_tsv(rows, include_header=not args.no_header))
        return 0

    print(_render_table(rows, include_header=not args.no_header))
    return 0
