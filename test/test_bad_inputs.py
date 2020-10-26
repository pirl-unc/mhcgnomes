from nose.tools import raises
from mhcgnomes import normalized_string, ParseError, parse, compact_string

@raises(ParseError)
def test_normalized_string_extra_text_after_allele():
    normalized_string("HLA-A*02:01 zipper")


@raises(ParseError)
def test_compact_string_extra_text_after_allele():
    compact_string("HLA-A*02:01 zipper")


@raises(ParseError)
def test_parse_extra_text_after_allele():
    parse("HLA-A*02:01 zipper")


def test_normalized_string_extra_text_after_allele_no_raise():
    result = normalized_string("HLA-A*02:01 zipper", raise_on_error=False)
    assert result is None

def test_compact_string_extra_text_after_allele_no_raise():
    result = compact_string("HLA-A*02:01 zipper", raise_on_error=False)
    assert result is None


def test_parse_extra_text_after_allele_no_raise():
    result = parse("HLA-A*02:01 zipper", raise_on_error=False)
    assert result is None





