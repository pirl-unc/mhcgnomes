"""DataFrames preserving one row per input and forwarding public parse options."""

from . import function_api
from .errors import ParseError
from .parse_outcome import OUTCOME_COLUMNS, parse_outcome_to_row


def dataframe_from_parsed_objects(parsed_objects, raise_on_error=True):
    """Build a DataFrame from an iterable of Result, ParseError, or None outcomes.

    Input order is preserved. 'input' uses each result's raw_string (None when
    unavailable). Common columns follow parse_outcome_to_row; legacy to_record
    columns, including full 'gene' and 'allele' names, remain extra columns.
    Haplotype is supported even though it has no record schema. Empty input
    returns an empty frame with OUTCOME_COLUMNS.

    With raise_on_error=True (default), ParseError/None outcomes raise
    ParseError. False retains them as error rows. Unsupported outcome types
    and unexpected serialization errors always propagate. pandas is imported
    only when a DataFrame is requested.
    """
    rows = []
    for outcome in parsed_objects:
        if raise_on_error and (outcome is None or isinstance(outcome, ParseError)):
            raise outcome if outcome is not None else ParseError("Missing parse result")
        rows.append(parse_outcome_to_row(getattr(outcome, "raw_string", None), outcome))
    return _dataframe_from_rows(rows)


def dataframe_from_string_list(names, raise_on_error=True, **parse_kwargs):
    """Parse an iterable of scalar names into one DataFrame row per input.

    All parse_kwargs are forwarded to mhcgnomes.parse, including species,
    use_allele_aliases, require_explicit_species and required_result_types.
    raise_on_error=True stops at the first ParseError; False retains errors
    and missing values as rows. Invalid input types still raise TypeError, and
    invalid options/programming errors are never swallowed. Input order and
    original values are preserved; a Series' index is not reused.

    Common columns are OUTCOME_COLUMNS from mhcgnomes.parse_outcome. Each
    successful result's to_record fields are retained as additional columns;
    'gene' keeps the full legacy identifier while 'gene_name' is short. Missing
    record fields use pandas' usual missing values. Haplotype still has common
    outcome columns. Empty input returns those common columns with zero rows.
    """
    rows = []
    for name in names:
        try:
            outcome = function_api.parse(name, raise_on_error=True, **parse_kwargs)
        except ParseError as error:
            if raise_on_error:
                raise
            outcome = error
        rows.append(parse_outcome_to_row(name, outcome))
    return _dataframe_from_rows(rows)


def _dataframe_from_rows(rows):
    import pandas as pd

    columns = list(OUTCOME_COLUMNS)
    columns.extend(dict.fromkeys(k for row in rows for k in row if k not in OUTCOME_COLUMNS))
    result = pd.DataFrame.from_records(rows, columns=columns)
    # Preserve original None/NaN/NA values without pandas' string inference.
    result["input"] = pd.Series([row["input"] for row in rows], dtype=object)
    return result
