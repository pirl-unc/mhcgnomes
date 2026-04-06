import pytest

from mhcgnomes import Serotype, Species, parse

from .common import eq_


def test_HLA_A2_in_species_serotype_dictionary():
    human = Species.get("HLA")
    assert human is not None
    assert "A2" in human.serotypes


def test_parse_HLA_A2_serotype():
    result = parse("HLA-A2")
    assert result is not None
    eq_(result.name, "A2")
    eq_(result.species.prefix, "HLA")


# ---- IEF/CTL dot-notation subtypes ----


@pytest.mark.parametrize(
    "name, expected_alleles",
    [
        # A2 IEF subtypes (van der Poel et al. 1983)
        ("A2.1", ["A*02:01"]),
        ("A2.2F", ["A*02:02"]),
        ("A2.2Y", ["A*02:05"]),
        ("A2.3", ["A*02:03"]),
        ("A2.4", ["A*02:04"]),
        ("A2.4a", ["A*02:06"]),
        ("A2.4b", ["A*02:07"]),
        ("A2.5", ["A*02:11"]),
        # B27 IEF subtypes (Rojo et al. 1985)
        ("B27.1", ["B*27:05"]),
        ("B27.2", ["B*27:02"]),
        ("B27.3", ["B*27:04"]),
        # B35 IEF subtypes (Yang et al. 1995)
        ("B35.1", ["B*35:08"]),
        ("B35.2", ["B*35:02", "B*35:04"]),
        ("B35.3", ["B*35:01", "B*35:03"]),
        # B7 IEF subtype (Grumet et al. 1995)
        ("B7.1", ["B*07:05"]),
    ],
)
def test_ief_dot_notation_serotypes(name, expected_alleles):
    """IEF/CTL dot-notation subtypes parse as serotypes with correct alleles."""
    result = parse(name)
    assert isinstance(result, Serotype), (
        f"Expected Serotype for '{name}' but got {type(result).__name__}: {result}"
    )
    eq_(result.name, name)
    actual_alleles = sorted(a.to_string(include_species=False) for a in result.alleles)
    eq_(actual_alleles, sorted(expected_alleles))
