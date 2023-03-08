from pytest import raises
from mhcgnomes import ParseError, parse

def test_parse_extra_text_after_allele():
    with raises(ParseError):
        parse("HLA-A*02:01 zipper")

def test_bad_input_parse_extra_text_after_allele():
    with raises(ParseError):
        parse("HLA-A*02:01 zipper")

def test_bad_input_parse_extra_text_after_allele_no_raise():
    result = parse("HLA-A*02:01 zipper", raise_on_error=False)
    assert result is None

def test_bad_input_parse_two_species():
    result = parse("HLA Calu", raise_on_error=False)
    assert result is None, result

def test_bad_input_only_MHC():
    result = parse("MHC", raise_on_error=False)
    assert result is None, result

def test_bad_input_only_MHC_in_three_words():
    result = parse("major histocompatibility complex", raise_on_error=False)
    assert result is None, result

def test_bad_input_only_numbers():
    result = parse("123", raise_on_error=False)
    assert result is None, result
