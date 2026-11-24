"""Tests for genus-level/trinomial CamelCase aliases (#274), case-insensitive
decorated scientific names (#205), and Species hierarchy navigation helpers."""

import pytest

from mhcgnomes import Allele, Gene, Species, parse
from mhcgnomes.data import species as raw_species_dict

from .common import eq_, ok_

# ---------------------------------------------------------------------------
# 1. Genus-level "<Taxon> sp." CamelCase aliases (#274)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_species,expected_string",
    [
        ("SusSp-1*01:01", "Sus sp.", "SLA-1*01:01"),
        ("BosSp-1*007:01", "Bos sp.", "BoLA-1*007:01"),
        ("CanisSp-12*001:01", "Canis sp.", "DLA-12*001:01"),
        ("FelisSp-E*003:01", "Felis sp.", "FLA-E*003:01"),
        ("OvisSp-DRB1*01:01", "Ovis sp.", "OLA-DRB1*01:01"),
        ("EquusSp-DRA*01:01", "Equus sp.", "ELA-DRA*01:01"),
        ("RattusSp-A1*01:01", "Rattus sp.", "RT1-A1*01:01"),
        ("RattusSp-Ba", "Rattus sp.", "RT1-Ba"),
        ("CoregonusSp-B1", "Coregonus sp.", "Cosp-B1"),
        ("TropheusSp-DDB1", "Tropheus sp.", "Trsp-DDB1"),
        ("TropheusSp-DDB2", "Tropheus sp.", "Trsp-DDB2"),
    ],
)
def test_genus_sp_camelcase_aliases_parse(raw, expected_species, expected_string):
    result = parse(raw, raise_on_error=True)
    assert isinstance(result, (Allele, Gene))
    eq_(result.species.name, expected_species)
    eq_(result.to_string(), expected_string)


def test_every_sp_entry_has_round_trippable_camelcase_alias():
    sp_entries = [name for name in raw_species_dict if name.endswith(" sp.")]
    assert len(sp_entries) >= 48
    for latin_name in sp_entries:
        genus = latin_name[:-4]
        expected_alias = genus[:1].upper() + genus[1:] + "Sp"
        resolved = Species.get(expected_alias)
        assert resolved is not None, f"Species.get({expected_alias!r}) returned None"
        eq_(resolved.name, latin_name)


@pytest.mark.parametrize(
    "query,expected_name",
    [
        ("Rattus sp", "Rattus sp."),
        ("rattus sp", "Rattus sp."),
        ("rattus_sp", "Rattus sp."),
        ("Mus sp", "Mus sp."),
        ("mus sp", "Mus sp."),
        ("Sus sp", "Sus sp."),
    ],
)
def test_genus_sp_without_trailing_period_resolves(query, expected_name):
    sp = Species.get(query)
    assert sp is not None, f"Species.get({query!r}) returned None"
    eq_(sp.name, expected_name)


def test_mus_sp_retains_prefix_inheritance_as_generated():
    mus_sp = Species.get_by_latin_name("Mus sp.")
    eq_(mus_sp.prefix_provenance, "generated")
    eq_(Species.get_by_latin_name("Mus musculus").old_mhc_prefix, "MusSp")


# ---------------------------------------------------------------------------
# 2. Trinomial CamelCase aliases (#274)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_species,expected_prefix",
    [
        ("CanisLupusBaileyi-DRB1*01:01", "Canis lupus baileyi", "Caba"),
        ("BalaenopteraMusculusBrevicauda-DQB*01:01", "Balaenoptera musculus brevicauda", "Bamubr"),
        ("StrixOccidentalisCaurina-DAB1*01:01", "Strix occidentalis caurina", "StriOccCaur"),
        ("SapajusApellaMacrocephalus-E*01:01", "Sapajus apella macrocephalus", "Sama"),
    ],
)
def test_trinomial_camelcase_aliases_parse(raw, expected_species, expected_prefix):
    result = parse(raw, raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.name, expected_species)
    eq_(result.species.prefix, expected_prefix)


# ---------------------------------------------------------------------------
# 3. Case-insensitive decorated scientific names (#205)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query,expected_name",
    [
        ("Canis lupus familiaris", "Canis lupus familiaris"),
        ("canis lupus familiaris", "Canis lupus familiaris"),
        ("CANIS LUPUS FAMILIARIS", "Canis lupus familiaris"),
        ("canis_lupus_familiaris", "Canis lupus familiaris"),
        ("Canis_lupus_familiaris", "Canis lupus familiaris"),
        ("Mus musculus domesticus", "Mus musculus"),
        ("mus musculus domesticus", "Mus musculus"),
        ("mus_musculus_domesticus", "Mus musculus"),
        ("Cyprinus carpio 'xingguonensis'", "Cyprinus carpio"),
        ("cyprinus carpio 'xingguonensis'", "Cyprinus carpio"),
        ("Strix occidentalis caurina (northern spotted owl)", "Strix occidentalis caurina"),
        ("strix occidentalis caurina (northern spotted owl)", "Strix occidentalis caurina"),
        ("Homo sapiens (Human)", "Homo sapiens"),
        ("homo sapiens (human)", "Homo sapiens"),
        ("Aquarana catesbeiana (American bullfrog)", "Lithobates catesbeianus"),
        ("Rattus sp (Norway rat)", "Rattus sp."),
    ],
)
def test_decorated_scientific_names_are_case_and_underscore_insensitive(query, expected_name):
    sp = Species.get(query)
    assert sp is not None, f"Species.get({query!r}) returned None"
    eq_(sp.name, expected_name)


@pytest.mark.parametrize(
    "bad_query",
    [
        "canis lupis",
        "canis lupis familiaris",
        "domestic cat invalid",
        "gray wolf pack",
        "human class I",
        "nonexistent species name",
    ],
)
def test_decorated_fallback_does_not_fuzzy_match_or_match_common_phrases(bad_query):
    assert Species.get(bad_query) is None


# ---------------------------------------------------------------------------
# 4. Species hierarchy navigation (FLA <-> Feca, BoLA <-> Bota) & is_cow
# ---------------------------------------------------------------------------


def test_species_children_descendants_and_ancestors():
    felis = Species.get("FLA")
    feca = Species.get("Feca")
    eq_(felis.children, (feca,))
    eq_(felis.descendants, (feca,))
    ok_(felis in feca.ancestors)
    ok_(felis.compatible_with(feca))
    eq_(parse("FLA-E*003:01", species="Felis catus").to_string(), "Feca-E*003:01")

    bos = Species.get("BoLA")
    bota = Species.get("Bota")
    ok_(bota in bos.children)
    ok_(bota in bos.descendants)
    ok_(bos in bota.ancestors)
    eq_(parse("BoLA-1*007:01", species="Bos taurus").to_string(), "Bota-1*007:01")

    primata = Species.get("Primata sp.")
    human = Species.get("Homo sapiens")
    nhp = Species.get("NHP")
    mamu = Species.get("Mamu")
    ok_(human in primata.children)
    ok_(nhp in primata.children)
    ok_(mamu in primata.descendants)
    ok_(mamu in nhp.descendants)
    ok_(human not in nhp.descendants)


def test_is_cow_matches_both_bola_and_bota():
    ok_(Species.get("BoLA").is_cow)
    ok_(Species.get("Bota").is_cow)
    ok_(Species.get("Bos taurus").is_cow)
    ok_(Species.get("cow").is_cow)
    ok_(not Species.get("Homo sapiens").is_cow)
