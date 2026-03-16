"""
Tests for Species identity model where latin name is the canonical identity
and prefixes/common names are aliases that may be ambiguous.
"""

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# 1. Species identity via latin name
# ---------------------------------------------------------------------------


def test_species_get_by_latin_name_human():
    species = Species.get_by_latin_name("Homo sapiens")
    assert species is not None
    eq_(species.prefix, "HLA")


def test_species_get_by_latin_name_mouse():
    species = Species.get_by_latin_name("Mus musculus")
    assert species is not None
    eq_(species.prefix, "H2")


def test_species_get_by_latin_name_chicken():
    species = Species.get_by_latin_name("Gallus gallus")
    assert species is not None
    eq_(species.prefix, "Gaga")


def test_species_get_by_latin_name_unknown_returns_none():
    assert Species.get_by_latin_name("Nonexistus fictionalus") is None


def test_species_latin_name_property():
    species = Species.get_by_latin_name("Homo sapiens")
    eq_(species.latin_name, "Homo sapiens")
    eq_(species.name, "Homo sapiens")


def test_species_to_record_includes_latin_name():
    species = Species.get_by_latin_name("Homo sapiens")
    record = species.to_record()
    assert "species_latin_name" in record
    eq_(record["species_latin_name"], "Homo sapiens")
    # Backwards compatibility
    assert "species_name" in record
    eq_(record["species_name"], "Homo sapiens")


# ---------------------------------------------------------------------------
# 2. Unique alias regression tests
# ---------------------------------------------------------------------------


def test_species_get_unique_prefix_still_works():
    for prefix, expected_name in [
        ("HLA", "Homo sapiens"),
        ("H2", "Mus musculus"),
        ("BoLA", "Bos sp."),
    ]:
        species = Species.get(prefix)
        assert species is not None, f"Species.get({prefix!r}) returned None"
        eq_(species.name, expected_name)


def test_species_get_unique_common_name_still_works():
    for name in ["human", "mouse"]:
        species = Species.get(name)
        assert species is not None, f"Species.get({name!r}) returned None"


def test_parse_unique_prefix_strings_unchanged():
    """Representative existing cases still parse identically."""
    examples = [
        ("HLA-A*02:01", Allele),
        ("Gaga-BF1", Gene),
        ("Dare-UBA", Gene),
    ]
    for raw, expected_type in examples:
        result = parse(raw, raise_on_error=True)
        assert isinstance(result, expected_type), (
            f"{raw} parsed as {type(result)}, expected {expected_type}"
        )


# ---------------------------------------------------------------------------
# 3. Ambiguity tests using real runtime collision (Bubu)
# ---------------------------------------------------------------------------


def test_species_get_multiple_bubu_returns_two_species():
    candidates = Species.get_multiple("Bubu")
    assert len(candidates) == 2
    names = {sp.name for sp in candidates}
    assert "Bubalus bubalis" in names
    assert "Bubo bubo" in names


def test_species_get_bubu_returns_none():
    """Bare Bubu must not silently resolve to one species."""
    assert Species.get("Bubu") is None


def test_parse_bare_bubu_is_ambiguous():
    """Bare ambiguous species token should not resolve to one species."""
    result = parse("Bubu", raise_on_error=False)
    assert result is None


def test_parse_bubu_dqa_resolves_water_buffalo():
    """Bubu-DQA should resolve to Bubalus bubalis via gene context."""
    result = parse("Bubu-DQA", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Bubalus bubalis")


def test_parse_bubu_dab1_resolves_eagle_owl():
    """Bubu-DAB1 should resolve to Bubo bubo via gene context."""
    result = parse("Bubu-DAB1", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Bubo bubo")


def test_parse_bubu_allele_resolves_by_gene_context():
    """Bubu-DQA*01:01 should resolve to buffalo via gene context."""
    result = parse("Bubu-DQA*01:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.name, "Bubalus bubalis")


def test_species_get_by_latin_name_buffalo():
    """Direct latin name lookup bypasses ambiguity."""
    species = Species.get_by_latin_name("Bubalus bubalis")
    assert species is not None
    eq_(species.prefix, "Bubu")


def test_species_get_by_latin_name_eagle_owl():
    """Direct latin name lookup bypasses ambiguity."""
    species = Species.get_by_latin_name("Bubo bubo")
    assert species is not None
    eq_(species.prefix, "Bubu")


# ---------------------------------------------------------------------------
# 4. Default species accepts latin name
# ---------------------------------------------------------------------------


def test_default_species_accepts_latin_name():
    """Parsing with default_species as latin name should work."""
    result = parse("A*02:01", default_species="Homo sapiens")
    assert result is not None
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
