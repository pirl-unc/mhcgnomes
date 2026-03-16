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


def test_species_get_bubu_resolves_to_buffalo():
    """Bubu is now uniquely owned by water buffalo (eagle-owl is BuboBubo)."""
    species = Species.get("Bubu")
    assert species is not None
    eq_(species.name, "Bubalus bubalis")


def test_parse_bubu_dqa_resolves_water_buffalo():
    """Bubu-DQA should resolve to Bubalus bubalis."""
    result = parse("Bubu-DQA", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Bubalus bubalis")


def test_parse_bubobubo_dab1_resolves_eagle_owl():
    """BuboBubo-DAB1 should resolve to eagle-owl via long prefix."""
    result = parse("BuboBubo-DAB1", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Bubo bubo")


def test_parse_bubu_allele_resolves_by_gene_context():
    """Bubu-DQA*01:01 should resolve to buffalo."""
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
    eq_(species.prefix, "BuboBubo")


def test_long_prefix_always_parseable():
    """The 5+5 long prefix should always work for parsing any species."""
    for latin, long_prefix in [
        ("Bubo bubo", "BuboBubo"),
        ("Chrysemys picta", "ChrysPicta"),
        ("Gavialis gangeticus", "GaviaGange"),
        ("Casuarius casuarius", "CasuaCasua"),
        ("Caretta caretta", "CaretCaret"),
    ]:
        species = Species.get(long_prefix)
        assert species is not None, f"Species.get({long_prefix!r}) returned None"
        eq_(species.name, latin)


def test_long_prefix_works_for_allele_parsing():
    """HomoSapie-A*02:01 should parse as HLA-A*02:01."""
    result = parse("HomoSapie-A*02:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
    eq_(result.gene.name, "A")
    eq_(result.allele_fields, ("02", "01"))


def test_long_prefix_works_for_compact_allele():
    """HomoSapie-A0201 should also parse."""
    result = parse("HomoSapie-A0201", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
    eq_(result.allele_fields, ("02", "01"))


def test_full_latin_name_concatenated_works():
    """HomoSapiens-A*02:01 should parse (full latin name, no truncation)."""
    result = parse("HomoSapiens-A*02:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
    eq_(result.gene.name, "A")
    eq_(result.allele_fields, ("02", "01"))


def test_full_latin_name_concatenated_various_species():
    """Full concatenated latin names should work for any species."""
    for concat, expected_prefix in [
        ("DanioRerio-UBA", "Dare"),
        ("GallusGallus-BF1", "Gaga"),
        ("MusMusculus-K", "H2"),
    ]:
        result = parse(concat, raise_on_error=True)
        assert result is not None, f"parse({concat!r}) returned None"
        eq_(result.species.prefix, expected_prefix)


def test_latin_name_with_space_works():
    """'Homo sapiens-A*02:01' with a space in the species name should work."""
    result = parse("Homo sapiens-A*02:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")


# ---------------------------------------------------------------------------
# 6. Failure modes for latin name / long prefix parsing
# ---------------------------------------------------------------------------


def test_nonexistent_latin_name_returns_none():
    assert parse("FictusSpecius-A*02:01", raise_on_error=False) is None


def test_partial_latin_name_too_short_returns_none():
    """Just 'Homo' should not resolve to a full allele."""
    assert parse("Homo-A*02:01", raise_on_error=False) is None


def test_misspelled_latin_name_returns_none():
    assert parse("HomoSapeins-A*02:01", raise_on_error=False) is None


def test_wrong_gene_for_species_returns_none():
    """HomoSapiens-BF1 — BF1 is a chicken gene, not human."""
    assert parse("HomoSapiens-BF1", raise_on_error=False) is None


# ---------------------------------------------------------------------------
# 4. Default species accepts latin name
# ---------------------------------------------------------------------------


def test_default_species_accepts_latin_name():
    """Parsing with default_species as latin name should work."""
    result = parse("A*02:01", default_species="Homo sapiens")
    assert result is not None
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
