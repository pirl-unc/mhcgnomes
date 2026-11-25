import pytest

from mhcgnomes import Allele, parse

from .common import eq_


def test_Popy_DRB_W116_01():
    seq = "Popy-DRB*W116:01"
    allele = parse(seq)
    eq_(allele, Allele.get("Popy", "DRB", "W116", "01"))


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Mane-DRB*W1:03", "Mane-DRB*W1:03"),
        ("Mane-DRB*W2:07", "Mane-DRB*W2:07"),
        ("Mane-DRB*W6:02", "Mane-DRB*W6:02"),
        ("Mane-DRB*W1", "Mane-DRB*W1"),
        ("Mamu-DRB*W2:01", "Mamu-DRB*W2:01"),
        ("Mamu-DRB*w2:01", "Mamu-DRB*W2:01"),
        ("Mafa-DRB*W1:01", "Mafa-DRB*W1:01"),
        ("Patr-DRB*W1:01", "Patr-DRB*W1:01"),
    ],
)
def test_single_digit_ipd_w_prefix_preserves_uppercase_W(raw, expected):
    """Single-digit IPD-MHC W-prefix lineages (DRB*W1..W9) must keep uppercase W (#297)."""
    allele = parse(raw, use_allele_aliases=False)
    eq_(allele.to_string(), expected)
    eq_(parse(allele.to_string(), use_allele_aliases=False), allele)


def test_single_digit_w_prefix_does_not_leak_into_hla():
    assert parse("HLA-B*w4", raise_on_error=False) is None
    assert parse("HLA-C*w01:02", raise_on_error=False) is None
