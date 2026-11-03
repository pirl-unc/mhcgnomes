import numpy as np
import pandas as pd
import pytest

from mhcgnomes import ParseError, Parser, infer_mhc_class, parse, parse_gene_class
from mhcgnomes.common import normalize_string
from mhcgnomes.input_validation import validate_mhc_input


@pytest.mark.parametrize(
    "missing", [None, float("nan"), np.float32("nan"), pd.NA, pd.NaT, np.datetime64("NaT", "ns")]
)
@pytest.mark.parametrize("entrypoint", [parse, parse_gene_class, Parser().parse])
def test_missing_values_follow_error_policy(missing, entrypoint):
    assert entrypoint(missing, raise_on_error=False) is None
    with pytest.raises(ParseError, match="Missing MHC name"):
        entrypoint(missing)
    assert infer_mhc_class(missing) is None


@pytest.mark.parametrize(
    "invalid",
    [
        123,
        0.0,
        float("inf"),
        True,
        b"HLA-A*02:01",
        ["HLA-A*02:01"],
        {},
        np.array(["HLA-A*02:01"]),
        object(),
    ],
)
@pytest.mark.parametrize("entrypoint", [parse, parse_gene_class, Parser().parse])
def test_invalid_types_are_never_coerced_or_hidden(invalid, entrypoint):
    for strict in (True, False):
        with pytest.raises(TypeError, match="expected str, got"):
            entrypoint(invalid, raise_on_error=strict)
    with pytest.raises(TypeError, match="expected str, got"):
        infer_mhc_class(invalid)


def test_validation_leaves_strings_unchanged_and_accepts_subclasses():
    class Name(str):
        pass

    assert validate_mhc_input("nan")
    assert validate_mhc_input("")
    assert parse(Name("HLA-A*02:01")) == parse("HLA-A*02:01")
    assert validate_mhc_input(None, raise_on_error=False) is False


def test_key_normalization_has_a_distinct_numeric_yaml_contract():
    assert normalize_string(12) == "12"
    assert normalize_string(1.5) == "1.5"
    assert normalize_string(None) is None
    for invalid in [True, b"HLA", [], {}]:
        with pytest.raises(TypeError, match="expected str, int, float or None"):
            normalize_string(invalid)
