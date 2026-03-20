"""
Tests that species= rejects unknown species and doesn't silently pass
when the requested species isn't in the ontology.
"""

from mhcgnomes import ParseError, parse

from .common import eq_

# --- Unknown species should error, not silently pass ---


def test_species_strict_unknown_species_returns_none():
    """species= with unknown species should return None (raise_on_error=False)."""
    assert parse("MHCIIB", species="Ciconia ciconia", raise_on_error=False) is None


def test_species_strict_unknown_species_raises():
    """species= with unknown species should raise ParseError."""
    try:
        parse("MHCIIB", species="Ciconia ciconia", raise_on_error=True)
        assert False, "Should have raised ParseError"
    except ParseError:
        pass


def test_species_strict_unknown_species_does_not_return_wrong_species():
    """MHCIIB + species=unknown must NOT return Tyto alba."""
    result = parse("MHCIIB", species="Alcedo atthis", raise_on_error=False)
    assert result is None


# --- Gene-to-species inference should not override species= ---


def test_species_strict_blb2_with_grouse():
    """Grouse is now in the ontology under Galliformes and inherits BLB2."""
    result = parse("BLB2", species="Lagopus scotica", raise_on_error=True)
    assert result is not None
    eq_(result.species.name, "Lagopus scotica")


def test_species_strict_bf2_with_guinea_fowl():
    assert parse("BF2", species="Numida meleagris", raise_on_error=False) is None


def test_species_strict_ddb1_with_cichlid():
    assert parse("DDB1", species="Tropheus moorii", raise_on_error=False) is None


def test_species_strict_uaa1_with_ricefish():
    """UAA1 is now on Actinopterygii — ricefish inherits it."""
    result = parse("UAA1", species="Oryzias dancena", raise_on_error=True)
    assert result is not None
    eq_(result.species.name, "Oryzias dancena")


def test_species_strict_ze_with_barbs():
    assert parse("ZE", species="Labeobarbus intermedius", raise_on_error=False) is None


# --- Known species + wrong gene still rejects ---


def test_species_strict_mhciib_with_known_ostrich_succeeds():
    """MHCIIB + species=ostrich → MhcClass(II, beta) for ostrich.
    MHCIIB is now a region label (class II beta), not a gene."""
    from mhcgnomes import MhcClass

    result = parse("MHCIIB", species="Struthio camelus", raise_on_error=False)
    assert result is not None
    assert isinstance(result, MhcClass)
    eq_(result.species.name, "Struthio camelus")


def test_species_strict_known_species_correct_gene_works():
    """DMA + species=ostrich should work (inherited from Gnathostomata)."""
    result = parse("DMA", species="Struthio camelus", raise_on_error=False)
    assert result is not None
    eq_(result.species.name, "Struthio camelus")
