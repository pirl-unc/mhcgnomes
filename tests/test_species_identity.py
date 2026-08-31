"""
Tests for Species identity model where latin name is the canonical identity
and prefixes/common names are aliases that may be ambiguous.
"""

from collections import defaultdict
from contextlib import contextmanager

import pytest

from mhcgnomes import Allele, Gene, ParseError, Species, parse
from mhcgnomes.common import normalize_string
from mhcgnomes.data import species as species_data
from mhcgnomes.species import _make_long_prefix, raw_species_dict

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


def test_full_scientific_prefix_always_parseable():
    """The concatenated binomial is the default generated alias for any species."""
    for latin, full_prefix in [
        ("Bubo bubo", "BuboBubo"),
        ("Chrysemys picta", "ChrysemysPicta"),
        ("Gavialis gangeticus", "GavialisGangeticus"),
        ("Casuarius casuarius", "CasuariusCasuarius"),
        ("Caretta caretta", "CarettaCaretta"),
    ]:
        species = Species.get(full_prefix)
        assert species is not None, f"Species.get({full_prefix!r}) returned None"
        eq_(species.name, latin)


def test_5_5_prefixes_are_no_longer_generated():
    """
    The 5+5 tier was removed in 3.42.0 (see issue #128). These forms were
    parseable up to 3.41.0 and are not any species' curated prefix, so they
    should now resolve to nothing rather than to a species.
    """
    for retired in ["ChrysPicta", "GaviaGange", "CasuaCasua", "CaretCaret", "HomoSapie"]:
        assert Species.get(retired) is None, f"{retired!r} still resolves"


def test_colliding_4_4_forms_are_never_auto_generated():
    """
    Three 4+4 forms are derivable from two binomials each. None is emitted as a
    generated alias, and since #134 neither claimant curates one as a plain
    alias either, so none of the three resolves on its own.

    A subspecies must not veto its parent's shorthand: CaniLupu and BalaMusc
    are derivable from a binomial and its own subspecies, and belong to the
    binomial.
    """
    from mhcgnomes.species import _GENERATED_LONG_PREFIX_COUNTS, _long_prefix_if_claimable

    for alias in ["ChryPict", "LaniColl", "LeucLeuc"]:
        eq_(_GENERATED_LONG_PREFIX_COUNTS[alias], 2)
        assert Species.get(alias) is None, f"{alias} resolves globally"

    for alias, latin_name in [("CaniLupu", "Canis lupus"), ("BalaMusc", "Balaenoptera musculus")]:
        eq_(_GENERATED_LONG_PREFIX_COUNTS[alias], 1)
        eq_(Species.get(alias).name, latin_name)
    assert _long_prefix_if_claimable("Canis lupus baileyi") is None


def test_trinomials_mint_no_generated_alias_at_all():
    """
    Neither the concatenated form nor the 4+4 shorthand, since both are built
    from the parent binomial's first two words. Before 3.42.0 the 4+4 branch
    had no arity guard, so "Strix occidentalis caurina" claimed "StriOcci".
    """
    for subspecies, shorthand, concatenated in [
        ("Strix occidentalis caurina", "StriOcci", "StrixOccidentalis"),
        ("Sapajus apella macrocephalus", "SapaApel", "SapajusApella"),
        ("Canis lupus baileyi", "CanisLupusBaileyi", "CanisLupusBaileyi"),
    ]:
        assert Species.get(shorthand) is None, f"{shorthand!r} resolves"
        assert Species.get(concatenated) is None, f"{concatenated!r} resolves"
        assert Species.get_by_latin_name(subspecies) is not None


def test_contested_4_4_forms_resolve_only_under_explicit_species():
    """
    A 4+4 form derivable from two species names neither of them. Up to 3.42.0
    one side curated it and won silently, so a caller who meant the golden
    pheasant and wrote ChryPict got a painted turtle. Both claimants now list
    it under `context only prefixes`, so a bare form fails and an explicit
    species= still resolves. See #134.
    """
    from mhcgnomes.species import find_matching_context_only_species_objects

    for form, claimants in [
        ("ChryPict", {"Chrysemys picta", "Chrysolophus pictus"}),
        ("LaniColl", {"Lanius collurio", "Lanius collaris"}),
        ("LeucLeuc", {"Leucogeranus leucogeranus", "Leuciscus leuciscus"}),
    ]:
        assert Species.get(form) is None, f"bare {form!r} still resolves"
        eq_(Species.get_multiple(form), ())
        eq_({s.name for s in find_matching_context_only_species_objects(form)}, claimants)
        for latin_name in claimants:
            result = parse(f"{form}-DAB1", species=latin_name, raise_on_error=False)
            assert result is not None, f"{form}-DAB1 not rescued by species={latin_name}"
            eq_(result.species.name, latin_name)


def test_explicit_short_prefixes_beat_generated_collision_aliases():
    explicit_owners = defaultdict(set)
    for latin_name, record in raw_species_dict.items():
        explicit_owners[normalize_string(record["prefix"])].add(latin_name)
        for alias in record.get("other prefixes", []) or []:
            explicit_owners[normalize_string(alias)].add(latin_name)

    for latin_name in raw_species_dict:
        alias = _make_long_prefix(latin_name)
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


def test_full_prefix_works_for_allele_parsing():
    """HomoSapiens-A*02:01 should parse as HLA-A*02:01."""
    result = parse("HomoSapiens-A*02:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
    eq_(result.gene.name, "A")
    eq_(result.allele_fields, ("02", "01"))


def test_full_prefix_works_for_compact_allele():
    """HomoSapiens-A0201 should also parse."""
    result = parse("HomoSapiens-A0201", raise_on_error=True)
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

# (prefix, species that resolves it globally, species holding it context-only)
#
# The global prefix goes to whichever side is actually used in print, not
# automatically to whichever side IPD-MHC designates. Caau-DAB and Caau-UFA
# appear in the cyprinid MHC literature while IPD holds no allele sequences
# for Canis aureus, so the goldfish resolves and the jackal's designation is
# reserved.
PREFIX_COLLISIONS = [
    ("Hymo", "Hylobates moloch", "Hypophthalmichthys molitrix"),
    ("Caau", "Carassius auratus", "Canis aureus"),
    ("Hyam", "Hybognathus amarus", "Hyperoodon ampullatus"),
]


@pytest.mark.parametrize("prefix,resolves_to,reserved_for", PREFIX_COLLISIONS)
def test_colliding_prefix_resolves_to_the_attested_species(prefix, resolves_to, reserved_for):
    species = Species.get(prefix)
    assert species is not None, prefix
    eq_(species.name, resolves_to)


@pytest.mark.parametrize("prefix,resolves_to,reserved_for", PREFIX_COLLISIONS)
def test_losing_side_keeps_prefix_as_context_only(prefix, resolves_to, reserved_for):
    from mhcgnomes.species import find_matching_context_only_species_objects

    names = {s.name for s in find_matching_context_only_species_objects(prefix)}
    assert reserved_for in names, (prefix, names)


@pytest.mark.parametrize("prefix,resolves_to,reserved_for", PREFIX_COLLISIONS)
def test_reserved_species_still_reachable_by_its_own_prefix(prefix, resolves_to, reserved_for):
    species = Species.get_by_latin_name(reserved_for)
    assert species is not None
    eq_(Species.get(species.prefix).name, reserved_for)


def test_published_goldfish_designations_still_parse():
    """
    Caau-DAB and Caau-UFA are published Carassius auratus designations, so
    Caau-* must keep resolving to the goldfish even though IPD-MHC designates
    Caau to Canis aureus.
    """
    eq_(Species.get("Caau").name, "Carassius auratus")
    for gene_name in ["DAB1", "DAB3", "UBA"]:
        eq_(parse(f"Caau-{gene_name}").species.name, "Carassius auratus")


def test_minnow_designations_still_parse():
    eq_(Species.get("Hyam").name, "Hybognathus amarus")
    eq_(parse("Hyam-DAB1").species.name, "Hybognathus amarus")


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


# ---------------------------------------------------------------------------
# Prefix provenance (issue #128)
# ---------------------------------------------------------------------------


def test_designated_is_never_inferred():
    """
    "designated" has to come from a curator who read a source, so no entry
    reporting it may be re-derivable from its latin name -- if it were, the
    deriver would have said "generated" and the curation would be redundant or
    wrong. Asserting membership in the value set instead would prove nothing:
    the loader rejects anything else, and the deriver returns literals.
    """
    from mhcgnomes.species import _derive_prefix_provenance, latin_name_to_species_object

    for species in latin_name_to_species_object.values():
        if species.prefix_provenance != "designated":
            continue
        derived = _derive_prefix_provenance(species.prefix, species.name)
        assert derived is None, (
            f"{species.name} is curated 'designated' but derivation says "
            f"{derived!r}; one of the two is wrong"
        )


def test_every_designated_prefix_cites_a_source():
    """
    CLAUDE.md: "Cite what you find in the YAML or code next to the change, with
    a PMID or URL." This is the one provenance value that is a claim about the
    outside world, so it is the one that must not ship uncited.
    """
    import re
    from pathlib import Path

    text = (Path(__file__).parent.parent / "mhcgnomes" / "data" / "species.yaml").read_text()
    declarations = re.findall(r"^  prefix source: designated$", text, re.M)
    cited = re.findall(r"(?:^  #[^\n]*\n)+^  prefix source: designated$", text, re.M)
    # Count first: an entry with no comment block at all matches the second
    # pattern zero times, so iterating matches alone would skip exactly the
    # case this test exists to catch.
    eq_(
        len(cited),
        len(declarations),
        f"{len(declarations) - len(cited)} 'prefix source: designated' declaration(s) "
        f"with no comment above them at all",
    )
    for comment in cited:
        assert "http" in comment or "PMID" in comment, (
            f"'prefix source: designated' with no citation:\n{comment}"
        )


def test_generated_prefixes_are_reported_as_generated():
    """A prefix mhcgnomes minted from the latin name is provable by derivation."""
    for latin_name, prefix in [
        ("Tachyglossus aculeatus", "TachAcul"),
        ("Abramis brama", "AbraBram"),
        ("Chrysemys picta", "ChrysemysPicta"),
    ]:
        species = Species.get_by_latin_name(latin_name)
        eq_(species.prefix, prefix)
        eq_(species.prefix_provenance, "generated")


def test_group_labels_are_reported_as_group_labels():
    """Aves, Galliformes and NHP name groupings and are never written on alleles."""
    for latin_name in ["Aves sp.", "Galliformes sp.", "Primata sp.", "NHP"]:
        eq_(Species.get_by_latin_name(latin_name).prefix_provenance, "group label")


def test_published_designations_are_curated_not_inferred():
    """
    These are marked in species.yaml with a source, because being absent from
    the generated forms does not prove a prefix is in published use -- the Caau
    case. Nothing infers "designated".
    """
    for latin_name, prefix in [
        ("Homo sapiens", "HLA"),
        ("Bos sp.", "BoLA"),
        ("Pan troglodytes", "Patr"),
        ("Macaca mulatta", "Mamu"),
    ]:
        species = Species.get_by_latin_name(latin_name)
        eq_(species.prefix, prefix)
        eq_(species.prefix_provenance, "designated")


def test_unestablished_provenance_stays_none():
    """
    Most short prefixes have not been checked against IPD/IMGT yet. They report
    None rather than being assumed published, so the gap is visible.
    https://github.com/pirl-unc/mhcgnomes/issues/131
    """
    from mhcgnomes.species import latin_name_to_species_object

    unknown = {s.name for s in latin_name_to_species_object.values() if s.prefix_provenance is None}
    assert unknown, "nothing left unestablished -- update this test if the sweep is finished"
    # Pinned by name rather than by count: #131 can then shrink the list one
    # entry at a time with a citation each, while a bulk assignment that sweeps
    # them all at once has to come here and say so. A count bound would have
    # done neither -- it fires on ordinary growth and passes a bulk assignment.
    for name in [
        "Aotus sp.",
        "Callithrix sp.",
        "Felis sp.",
        "Gorilla sp.",
        "Macaca sp.",
        "Oryctolagus sp.",
        "Pan sp.",
        "Pongo sp.",
    ]:
        assert name in unknown, (
            f"{name} was given a provenance -- if that is a checked fact, cite "
            f"the source in species.yaml and drop it from this list"
        )


@contextmanager
def temporary_species_entry(latin_name, entry):
    """
    Add an entry to the loaded ontology for the body of a test and take it out
    again, so a failing assertion cannot leave a synthetic species behind for
    the rest of the session.
    """
    from mhcgnomes.species import raw_species_dict

    raw_species_dict[latin_name] = entry
    try:
        yield
    finally:
        del raw_species_dict[latin_name]


def test_unknown_species_yaml_keys_are_rejected():
    """
    A misspelled key used to load silently, so species.yaml could assert
    something the runtime never read -- `prefix_source` instead of
    `prefix source` being the case that motivated this.
    """
    from mhcgnomes.species import SPECIES_ENTRY_KEYS, create_species_for_latin_name

    assert "prefix source" in SPECIES_ENTRY_KEYS
    assert "prefix_source" not in SPECIES_ENTRY_KEYS

    entry = {"prefix": "TestTypo", "name": "test", "prefix_source": "designated"}
    with (
        temporary_species_entry("Test typo sp.", entry),
        pytest.raises(ValueError, match="Unknown key"),
    ):
        create_species_for_latin_name("Test typo sp.")


def test_invalid_prefix_source_value_is_rejected():
    from mhcgnomes.species import create_species_for_latin_name

    # A string outside the value set, and the list form a curator would reach
    # for when adding a second citation -- which used to raise an unhandled
    # TypeError at import, naming no species.
    for bad_value in ["attested", ["designated"]]:
        entry = {"prefix": "TestValue", "name": "test", "prefix source": bad_value}
        with (
            temporary_species_entry("Test value sp.", entry),
            pytest.raises(ValueError, match="prefix source"),
        ):
            create_species_for_latin_name("Test value sp.")


def test_4_4_shorthand_parses_an_allele():
    """
    The tier README.md documents as `HomoSapi-A*02:01`. Both allele-parse tests
    above use the concatenated form, so without this nothing covers the 4+4
    branch and a regression in its uniqueness guard would drop the whole tier
    silently.
    """
    result = parse("HomoSapi-A*02:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "HLA")
    eq_(result.gene.name, "A")
    eq_(result.allele_fields, ("02", "01"))
