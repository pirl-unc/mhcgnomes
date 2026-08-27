"""
Tests for Species identity model where latin name is the canonical identity
and prefixes/common names are aliases that may be ambiguous.
"""

from collections import defaultdict

import pytest

from mhcgnomes import Allele, Gene, ParseError, Species, parse
from mhcgnomes.common import normalize_string
from mhcgnomes.data import species as species_data
from mhcgnomes.species import _make_5_5_prefix, _make_long_prefix, raw_species_dict

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


def test_all_species_prefixes_and_other_prefixes_are_unique_after_normalization():
    owners_by_prefix = defaultdict(set)
    for latin_name, record in species_data.items():
        prefix = record.get("prefix")
        if prefix:
            owners_by_prefix[normalize_string(prefix)].add(latin_name)
        for alias in record.get("other prefixes", []) or []:
            owners_by_prefix[normalize_string(alias)].add(latin_name)

    collisions = {
        prefix: sorted(owners) for prefix, owners in owners_by_prefix.items() if len(owners) > 1
    }
    assert collisions == {}


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


def test_parse_lanicola_species_resolves_fiscal_shrike():
    species = Species.get("LaniCola")
    assert species is not None
    eq_(species.name, "Lanius collaris")


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


def test_generated_4_4_prefix_collisions_are_not_global_aliases():
    for alias in ["CaniLupu"]:
        assert Species.get(alias) is None
        assert Species.get_multiple(alias) == ()


def test_generated_5_5_prefix_collisions_fall_back_to_full_scientific_name():
    assert Species.get("CanisLupus") is not None
    eq_(Species.get("CanisLupus").name, "Canis lupus")
    assert Species.get("CanisLupusBaileyi") is None


def test_curated_prefix_keeps_global_owner_when_generated_alias_would_collide():
    for prefix, latin_name in [
        ("ChryPict", "Chrysemys picta"),
        ("LaniColl", "Lanius collurio"),
    ]:
        species = Species.get(prefix)
        assert species is not None
        eq_(species.name, latin_name)


def test_explicit_short_prefixes_beat_generated_collision_aliases():
    explicit_owners = defaultdict(set)
    for latin_name, record in raw_species_dict.items():
        explicit_owners[normalize_string(record["prefix"])].add(latin_name)
        for alias in record.get("other prefixes", []) or []:
            explicit_owners[normalize_string(alias)].add(latin_name)

    for generator in (_make_long_prefix, _make_5_5_prefix):
        for latin_name in raw_species_dict:
            alias = generator(latin_name)
            if not alias:
                continue
            owners = explicit_owners.get(normalize_string(alias))
            if not owners:
                continue
            species = Species.get(alias)
            assert species is not None
            assert species.name in owners


def test_trinomial_entries_do_not_get_full_concatenated_aliases():
    wolf = Species.get("CanisLupus")
    assert wolf is not None
    eq_(wolf.name, "Canis lupus")
    assert Species.get("CanisLupusBaileyi") is None


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


def test_decorated_scientific_name_falls_back_to_base_binomial():
    decorated = "Cyprinus carpio 'xingguonensis'"
    species = Species.get(decorated)
    assert species is not None
    eq_(species, Species.get("Cyprinus carpio"))


def test_parenthetical_scientific_name_falls_back_to_exact_subspecies_when_present():
    decorated = "Strix occidentalis caurina (northern spotted owl)"
    species = Species.get(decorated)
    assert species is not None
    eq_(species, Species.get("Strix occidentalis caurina"))


def test_unmodeled_trinomial_falls_back_to_base_binomial():
    species = Species.get("Canis lupus familiaris")
    assert species is not None
    eq_(species, Species.get("Canis lupus"))


def test_sourced_short_2_2_prefix_alias_resolves_species():
    for short_prefix, latin_name in [
        ("Abbr", "Abramis brama"),
        ("Crin", "Crocodylus intermedius"),
        ("Crjo", "Crocodylus johnstoni"),
        ("Crpa", "Crocodylus palustris"),
        ("Crrh", "Crocodylus rhombifer"),
        ("Euma", "Eublepharis macularius"),
        ("Geja", "Gekko japonicus"),
        ("Lili", "Limosa limosa"),
        ("Pato", "Parachondrostoma toxostoma"),
        ("Ruru", "Rutilus rutilus"),
        ("Spsp", "Spinus spinus"),
        ("Tycu", "Tympanuchus cupido"),
    ]:
        species = Species.get(short_prefix)
        assert species is not None, f"Species.get({short_prefix!r}) returned None"
        eq_(species.name, latin_name)


def test_sourced_short_2_2_prefix_alias_parses_genes():
    for raw, expected_prefix, expected_gene in [
        ("Abbr-DAB1", "AbraBram", "DAB1"),
        ("Crin-DB05", "CrocInte", "DB05"),
        ("Crjo-DB02", "CrocJohn", "DB02"),
        ("Crpa-DB02", "CrocPalu", "DB02"),
        ("Crrh-DB05", "CrocRhom", "DB05"),
        ("Lili-UA", "LimoLimo", "UA"),
        ("Pato-DAB1", "ParaToxo", "DAB1"),
        ("Ruru-DAB3", "RutiRuti", "DAB3"),
        ("Spsp-UA", "SpinSpin", "UA"),
    ]:
        result = parse(raw, raise_on_error=True)
        assert isinstance(result, Gene)
        eq_(result.species.prefix, expected_prefix)
        eq_(result.name, expected_gene)


def test_collision_backed_short_prefix_remains_blocked():
    # Hymo is source-backed for silver carp, but runtime already owns it.
    species = Species.get("Hymo")
    assert species is not None
    eq_(species.name, "Hylobates moloch")
    assert parse("Hymo-UA", raise_on_error=False) is None


def test_existing_prefix_owner_wins_over_source_backed_short_alias():
    # Orla is used by multiple fish datasets and also collides with orangutan.
    species = Species.get("Orla")
    assert species is not None
    eq_(species.name, "Pongo sp.")
    assert parse("Orla-UGA", raise_on_error=False) is None


def test_orla_still_parses_as_orangutan():
    result = parse("OrLA-A*01:01", raise_on_error=True)
    eq_(result.species.name, "Pongo sp.")
    eq_(result.gene.name, "A")


def test_ambiguous_or_unsourced_short_prefixes_are_not_added():
    for short_prefix in [
        "Moal",  # reused across Monopterus albus and Motacilla alba
    ]:
        assert Species.get(short_prefix) is None
        assert parse(f"{short_prefix}-DAB", raise_on_error=False) is None


def test_context_only_prefixes_stay_out_of_global_species_lookup():
    assert Species.get("Moal") is None
    assert Species.get("Motacilla alba") is not None
    eq_(Species.get("Motacilla alba").prefix, "MotaAlba")


def test_context_only_hymo_failure_is_informative():
    with pytest.raises(ParseError, match="Hypophthalmichthys molitrix"):
        parse("Hymo-DAB", raise_on_error=True)


def test_context_only_moal_failure_is_informative():
    with pytest.raises(ParseError, match="Monopterus albus"):
        parse("Moal-DAB", raise_on_error=True)
    with pytest.raises(ParseError, match="Motacilla alba"):
        parse("Moal-DAB", raise_on_error=True)


def test_context_only_orla_failure_is_informative():
    with pytest.raises(ParseError, match=r"Pongo sp\."):
        parse("ORLA-UAA", raise_on_error=True)
    with pytest.raises(ParseError, match="Oryzias latipes"):
        parse("ORLA-UAA", raise_on_error=True)


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


# ---------------------------------------------------------------------------
# 5. Prefixes that two species can legitimately derive
#
# The Klein 2+2 scheme (first two letters of genus + first two of species)
# produces collisions. Where IPD-MHC has designated a species, that species
# owns the prefix globally and the other keeps it as a context-only alias --
# the pattern already used for Hymo (Hylobates moloch vs the silver carp).
# https://github.com/pirl-unc/mhcgnomes/issues/112
# ---------------------------------------------------------------------------

# (prefix, species IPD-MHC designates, species that keeps it context-only)
IPD_DESIGNATED_PREFIX_COLLISIONS = [
    ("Hymo", "Hylobates moloch", "Hypophthalmichthys molitrix"),
    ("Caau", "Canis aureus", "Carassius auratus"),
    ("Hyam", "Hyperoodon ampullatus", "Hybognathus amarus"),
]


@pytest.mark.parametrize("prefix,ipd_species,context_only", IPD_DESIGNATED_PREFIX_COLLISIONS)
def test_ipd_designated_species_owns_the_prefix(prefix, ipd_species, context_only):
    species = Species.get(prefix)
    assert species is not None, prefix
    eq_(species.name, ipd_species)


@pytest.mark.parametrize("prefix,ipd_species,context_only", IPD_DESIGNATED_PREFIX_COLLISIONS)
def test_colliding_species_keeps_prefix_as_context_only(prefix, ipd_species, context_only):
    from mhcgnomes.species import find_matching_context_only_species_objects

    names = {s.name for s in find_matching_context_only_species_objects(prefix)}
    assert context_only in names, (prefix, names)


@pytest.mark.parametrize("prefix,ipd_species,context_only", IPD_DESIGNATED_PREFIX_COLLISIONS)
def test_context_only_species_still_reachable_by_its_own_prefix(prefix, ipd_species, context_only):
    species = Species.get_by_latin_name(context_only)
    assert species is not None
    eq_(Species.get(species.prefix).name, context_only)


def test_caau_is_the_golden_jackal_not_a_goldfish():
    """IPD-MHC assigns Caau to Canis aureus; it used to resolve to Carassius auratus."""
    eq_(Species.get("Caau").name, "Canis aureus")
    eq_(parse("Caau-DRB1").species.name, "Canis aureus")


def test_hyam_is_the_bottlenose_whale_not_a_minnow():
    """IPD-MHC assigns Hyam to Hyperoodon ampullatus."""
    eq_(Species.get("Hyam").name, "Hyperoodon ampullatus")


# ---------------------------------------------------------------------------
# 6. Historic prefixes must not be claimed twice
# https://github.com/pirl-unc/mhcgnomes/issues/110
# ---------------------------------------------------------------------------


def test_pren_resolves_to_the_langur():
    """
    Pren is Presbytis entellus, the former name of Semnopithecus entellus.
    Theropithecus gelada also carried it, which made the prefix ambiguous.
    """
    eq_(Species.get("Pren").name, "Semnopithecus entellus")
    eq_(parse("Pren").name, "Semnopithecus entellus")


def test_pren_class_one_agrees_with_bare_pren():
    eq_(parse("Pren class I").species, Species.get("Pren"))


def test_gelada_still_reachable_by_its_own_prefix():
    eq_(parse("Thge-DQA1").species.name, "Theropithecus gelada")


def test_no_prefix_is_claimed_by_two_species():
    """
    Canonical prefixes, historic 'old prefix' values and 'other prefixes' all
    feed the same global alias table, so none of them may name two species.
    Context-only prefixes are deliberately excluded -- they exist precisely to
    hold the losing side of a collision.
    """
    claims = defaultdict(set)
    for latin_name, record in species_data.items():
        for key in ("prefix", "old prefix"):
            value = record.get(key)
            if value:
                claims[normalize_string(value)].add(latin_name)
        for value in record.get("other prefixes", []) or []:
            claims[normalize_string(value)].add(latin_name)
    collisions = {p: sorted(v) for p, v in claims.items() if len(v) > 1}
    assert collisions == {}
