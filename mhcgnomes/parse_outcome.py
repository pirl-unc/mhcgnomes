"""Public row representation shared by Python tables and command-line rendering."""

from .errors import ParseError
from .result import Result

OUTCOME_COLUMNS = (
    "input",
    "type",
    "normalized",
    "compact",
    "species",
    "gene_name",
    "mhc_class",
    "properties",
    "error",
)


def _stringify(value):
    if value is None:
        return ""
    if isinstance(value, (set, frozenset)):
        return ",".join(sorted(_stringify(x) for x in value))
    if isinstance(value, (list, tuple)):
        return ",".join(_stringify(x) for x in value)
    if isinstance(value, dict):
        return ",".join(f"{k}:{_stringify(v)}" for k, v in value.items())
    return str(value)


def parse_outcome_to_row(raw_input, outcome):
    """Return a new flat dict for an input and Result, ParseError, or None.

    Common fields are OUTCOME_COLUMNS. Successful rows contain normalized and
    compact text, result type, display species prefix, short gene_name, MHC
    class, formatted properties, and an empty error. Original to_record fields
    are retained, including its full gene identifier in 'gene'. No record fields
    are available when to_record raises NotImplementedError (e.g. Haplotype),
    but the common outcome fields still describe that result.

    A ParseError supplies the error message. None denotes an unsuccessful parse
    with a generic message. Error rows have type='ParseError', blank result
    fields, and the same message in error and properties. Input is retained
    unchanged, including scalar missing values. This function does not parse,
    validate raw_input or mutate outcome. Unsupported outcome types raise
    TypeError; unexpected serialization errors propagate.
    """
    row = dict.fromkeys(OUTCOME_COLUMNS, "")
    row["input"] = raw_input
    if outcome is None or isinstance(outcome, ParseError):
        message = str(outcome) if outcome is not None else f"Could not parse {raw_input!r}"
        row.update(type="ParseError", properties=message, error=message)
        return row
    if not isinstance(outcome, Result):
        raise TypeError(f"expected Result, ParseError or None, got {type(outcome).__name__}")
    try:
        record = outcome.to_record()
    except NotImplementedError:
        record = {}
    row.update(record)
    row.update(
        input=raw_input,
        type=type(outcome).__name__,
        normalized=outcome.to_string(),
        compact=outcome.compact_string(),
        species=_stringify(getattr(outcome, "species_prefix", "")),
        gene_name=_stringify(getattr(outcome, "gene_name", "")),
        mhc_class=record.get("mhc_class", getattr(outcome, "mhc_class", "")),
        properties="; ".join(f"{k}={_stringify(v)}" for k, v in record.items()),
        error="",
    )
    return row
