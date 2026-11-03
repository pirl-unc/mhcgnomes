"""Shared validation of scalar inputs to the public parsing APIs."""

from .errors import ParseError


def validate_mhc_input(value, raise_on_error=True):
    """Return True for strings, False for tolerated scalar missing values.

    None and scalar values recognized by pandas.isna (including float NaN,
    pandas.NA and NaT) are missing. With raise_on_error=True they raise
    ParseError instead. Other non-string values always raise TypeError; arrays,
    containers, bytes, booleans and ordinary numbers are never coerced to names.
    String subclasses are accepted. Strings, including empty strings and the
    literal 'nan', are passed unchanged to the parser.

    Intended for parse entrypoints and callers implementing the same input
    policy. Validation happens before caching or tokenization. pandas is loaded
    only when a non-string, non-None input needs a scalar missing-value check.
    """
    if isinstance(value, str):
        return True
    if value is None:
        missing = True
    else:
        from pandas import isna
        from pandas.api.types import is_scalar

        missing = is_scalar(value) and isna(value)
    if missing:
        if raise_on_error:
            raise ParseError("Missing MHC name")
        return False
    raise TypeError(f"expected str, got {type(value).__name__}")
