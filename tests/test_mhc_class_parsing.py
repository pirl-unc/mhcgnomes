import pytest

from mhcgnomes import (
    MhcClass,
    parse,
)


@pytest.mark.parametrize(
    "s",
    [
        "human class 1",
        "human class i",
        "human class I",
        "hla class 1",
        "hla class i",
        "hla class I",
        "HLA class 1",
        "HLA class i",
        "HLA class I",
    ],
)
def test_human_class_1(s):
    """Test parsing of human class I MHC strings."""
    expected_parsed_result = MhcClass.get("HLA", "I")
    expected_string_repr = "human class I"
    parsed_result = parse(s)
    assert parsed_result == expected_parsed_result, (
        f"Expected {expected_parsed_result} for parsing of '{s}' but got {parsed_result}"
    )
    normalized_str = parsed_result.to_string()
    assert normalized_str == expected_string_repr, (
        f"Expected '{expected_string_repr}' for normalized representation of '{s}' "
        f"but got '{normalized_str}'"
    )
    compact_str = parsed_result.compact_string()
    assert compact_str == expected_string_repr, (
        f"Expected '{expected_string_repr}' for compact representation of '{s}' "
        f"but got '{compact_str}'"
    )
