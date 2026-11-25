"""
Guard against bare UniProt protein accessions being misparsed as MHC alleles.

See https://github.com/pirl-unc/mhcgnomes/issues/306 and
https://www.uniprot.org/help/accession_numbers.
"""

import pytest

from mhcgnomes import ParseError, Parser, parse

from .common import eq_


@pytest.mark.parametrize(
    "accession",
    [
        # Japanese medaka (Oryzias latipes) accessions previously misparsed as mouse H2-L*r16..r44
        "H2LR16",
        "H2LR18",
        "H2LR19",
        "H2LR42",
        "H2LR44",
        # Mammalian P##### accessions previously misparsed as human HLA-P*NN:NNN
        "P01898",
        "P06339",
        "P14429",
        "P15978",
        "P70527",
        "P79568",
        # Isoform suffix form
        "P01898-2",
        # Other standard 6-char and 10-char UniProt accessions
        "Q6I7L2",
        "G3V1L5",
        "O19477",
        "A0A061HWC8",
    ],
)
def test_bare_uniprot_accessions_do_not_parse(accession):
    assert parse(accession, raise_on_error=False) is None
    assert parse(accession, species="Mus musculus", raise_on_error=False) is None
    assert parse(accession, species="Homo sapiens", raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(accession, raise_on_error=True)

    parser = Parser()
    eq_(parser.parse_multiple_candidates(accession), [])
    eq_(parser.parse_explicit_species_allele_candidates(accession), [])


@pytest.mark.parametrize(
    "valid_mhc,expected",
    [
        # Mixed-case compact mouse names stay parseable
        ("H2Kbm1", "H2-K*bm1"),
        ("H2Ddm1", "H2-D*dm1"),
        ("H2Ldm1", "H2-L*dm1"),
        ("H2IAg7", "H2-AA*d/AB*g7"),
        ("H2-Kbm1", "H2-K*bm1"),
        ("H2-L*r16", "H2-L*r16"),
        # Standard compact and explicit HLA names stay parseable
        ("A0201", "HLA-A*02:01"),
        ("B15112", "HLA-B*15:112"),
        ("P*01:01", "HLA-P*01:01"),
        ("HLA-P*01:01", "HLA-P*01:01"),
        ("HLA-P*01:898", "HLA-P*01:898"),
    ],
)
def test_uniprot_guard_preserves_valid_mhc_names(valid_mhc, expected):
    result = parse(valid_mhc)
    eq_(result.to_string(), expected)
