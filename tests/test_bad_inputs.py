import pytest

from mhcgnomes import Haplotype, ParseError, parse

from .common import eq_, raises


@raises(ParseError)
def test_parse_extra_text_after_allele():
    parse("HLA-A*02:01 zipper")


@raises(ParseError)
def test_bad_input_parse_extra_text_after_allele():
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


# ---------------------------------------------------------------------------
# Null markers and punctuation-only strings
# https://github.com/pirl-unc/mhcgnomes/issues/102
#
# These are how a curator or an exported spreadsheet writes "missing". They
# used to fall through to the default species and come back as a confident
# result -- "-" as Homo sapiens, "n/a" as the rat haplotype RT1-n/A.
# ---------------------------------------------------------------------------

NULL_MARKERS = [
    "n/a",
    "N/A",
    "n/A",
    "N/a",
    "-",
    "--",
    "---",
    "\u2014",  # em dash
    "\u2013",  # en dash
    ".",
    "..",
    "...",
    "*",
    "**",
    ",",
    ";",
    ":",
    "|",
    "_",
    "/",
    "//",
    " - ",
]


@pytest.mark.parametrize("marker", NULL_MARKERS)
def test_null_marker_does_not_parse(marker):
    assert parse(marker, raise_on_error=False) is None


@pytest.mark.parametrize("marker", NULL_MARKERS)
def test_null_marker_raises_when_asked(marker):
    with pytest.raises(ParseError):
        parse(marker)


def test_punctuation_only_strings_do_not_parse():
    """
    An MHC name has to carry at least one letter or digit. 254 punctuation-only
    strings used to come back as Homo sapiens.
    """
    punctuation = "-_./\\|,;:*+#~ "
    for first in punctuation:
        for second in punctuation:
            token = first + second
            assert parse(token, raise_on_error=False) is None, token


# The null-marker guard must not swallow real haplotype shorthand, which is
# genuinely written with a slash and bare letters in the mouse literature.


def test_bare_haplotype_pair_still_parses():
    result = parse("b/d")
    eq_(type(result), Haplotype)
    eq_(result.name, "b/d")
    assert result.is_mouse


def test_bare_single_letter_haplotype_still_parses():
    eq_(parse("d").name, "d")
    eq_(parse("n").name, "n")


def test_bare_single_letter_gene_still_parses():
    eq_(parse("a").to_string(), "HLA-A")
