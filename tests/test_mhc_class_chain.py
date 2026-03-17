"""
Tests for MHC class + chain parsing (MHCIIB, MHCIIA, mhc2b, mhc1, etc.).

These are region labels meaning "class N [alpha/beta], unknown locus"
and should parse as MhcClass with an optional chain restriction,
NOT as Gene objects.
"""

from mhcgnomes import MhcClass, parse

from .common import eq_

# --- Class II beta forms ---


def test_mhciib_uppercase():
    r = parse("MHCIIB", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "II")
    eq_(r.chain, "beta")


def test_mhciib_lowercase():
    r = parse("mhciib", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.chain, "beta")


def test_mhciib_mixed_case():
    r = parse("MhcIIB", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.chain, "beta")


def test_mhc_dash_iib():
    r = parse("MHC-IIB", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.chain, "beta")


def test_mhc2b():
    r = parse("mhc2b", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "II")
    eq_(r.chain, "beta")


# --- Class II alpha forms ---


def test_mhciia():
    r = parse("MHCIIA", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "II")
    eq_(r.chain, "alpha")


def test_mhc2a():
    r = parse("mhc2a", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.chain, "alpha")


# --- Class I (no chain) ---


def test_mhc1():
    r = parse("mhc1", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "I")
    eq_(r.chain, None)


def test_mhci():
    r = parse("MHCI", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "I")
    eq_(r.chain, None)


def test_mhcii_no_chain():
    r = parse("MHCII", default_species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.mhc_class, "II")
    eq_(r.chain, None)


# --- Output ---


def test_mhciib_to_string_includes_chain():
    r = parse("MHCIIB", default_species="Struthio camelus")
    eq_(r.to_string(), "ostrich class II beta")
    eq_(r.to_string(include_species=False), "class II beta")


def test_mhciia_to_string():
    r = parse("MHCIIA", default_species="Homo sapiens")
    eq_(r.to_string(), "human class II alpha")


def test_mhc1_to_string_no_chain():
    r = parse("mhc1", default_species="Homo sapiens")
    eq_(r.to_string(), "human class I")


# --- to_record ---


def test_mhciib_to_record_includes_chain():
    r = parse("MHCIIB", default_species="Struthio camelus")
    record = r.to_record()
    eq_(record["mhc_class"], "II")
    eq_(record["chain"], "beta")


def test_mhci_to_record_no_chain():
    r = parse("MHCI", default_species="Homo sapiens")
    record = r.to_record()
    eq_(record["mhc_class"], "I")
    assert "chain" not in record


# --- species= works with MHCIIB ---


def test_mhciib_with_species_strict():
    r = parse("MHCIIB", species="Struthio camelus")
    assert isinstance(r, MhcClass)
    eq_(r.species.name, "Struthio camelus")


def test_mhciib_with_unknown_species_errors():
    assert parse("MHCIIB", species="Ciconia ciconia", raise_on_error=False) is None


# --- Things that should NOT parse as MHC region labels ---


def test_bare_alpha_does_not_parse_as_mhc_region():
    """'alpha' alone should not become MhcClass."""
    r = parse("alpha", default_species="Homo sapiens", raise_on_error=False)
    assert not isinstance(r, MhcClass) or r is None


def test_bare_beta_does_not_parse_as_mhc_region():
    r = parse("beta", default_species="Homo sapiens", raise_on_error=False)
    assert not isinstance(r, MhcClass) or r is None


def test_mhciii_does_not_parse():
    """MHC class III is not a real adaptive immunity class."""
    r = parse("MHCIII", default_species="Homo sapiens", raise_on_error=False)
    assert r is None


def test_mhc3_does_not_parse():
    r = parse("mhc3", default_species="Homo sapiens", raise_on_error=False)
    assert r is None


def test_mhciic_does_not_parse():
    """MHCIIC — no 'C' chain exists."""
    r = parse("MHCIIC", default_species="Homo sapiens", raise_on_error=False)
    assert r is None
