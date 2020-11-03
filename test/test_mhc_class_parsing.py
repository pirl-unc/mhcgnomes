from mhcgnomes import (
    parse,
    MhcClass,
)
from nose.tools import eq_


def check_human_class1_string(s):
    expected_parsed_result = MhcClass.get("HLA", "I")
    expected_string_repr = "human class I"
    parsed_result = parse(s)
    eq_(
        parsed_result,
        expected_parsed_result,
        "Expected %s for parsing of '%s' but got %s" % (
            expected_parsed_result,
            s,
            parsed_result))
    normalized_str = parsed_result.to_string()
    eq_(
        normalized_str,
        expected_string_repr,
        "Expected '%s' for normalized representation of '%s' but got '%s'" % (
            expected_string_repr,
            s,
            normalized_str))
    compact_str = parsed_result.compact_string()
    eq_(
        compact_str,
        expected_string_repr,
        "Expected '%s' for compact representation of '%s' but got '%s'" % (
            expected_string_repr,
            s,
            compact_str))


def test_human_class_1():
    human_class1_strings = [
        "human class 1",
        "human class i",
        "human class I",
        "hla class 1",
        "hla class i",
        "hla class I",
        "HLA class 1",
        "HLA class i",
        "HLA class I",
    ]
    for s in human_class1_strings:
        yield check_human_class1_string, s
