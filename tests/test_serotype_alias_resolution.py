"""Alias mode must not over-specify compact two-field serotype assignments (#256)."""

import pytest

from mhcgnomes import Parser, Serotype, Species, parse
from mhcgnomes.data import haplotypes, heterodimers, serotypes, supertypes
from mhcgnomes.normalizing_dictionary import NormalizingDictionary


def test_hla_b44_does_not_overspecify_in_alias_mode():
    off = parse("HLA-B44", use_allele_aliases=False)
    on = parse("HLA-B44", use_allele_aliases=True)
    assert off.alleles[0].to_string() == "HLA-B*44:02"
    assert on.alleles[0].to_string() == "HLA-B*44:02"
    assert parse("HLA-B*44:02", use_allele_aliases=True).to_string() == "HLA-B*44:02"
    # Direct historical compact input still resolves opt-in historical aliases
    assert parse("HLA-B*4402", use_allele_aliases=True).to_string() == "HLA-B*44:02:01:01"


def test_hla_b15_preserves_three_digit_second_field_allele_in_alias_mode():
    """B*15112 in serotypes.yaml came from B*15:112, not historical B*15:11:02."""
    off = parse("HLA-B15", use_allele_aliases=False)
    on = parse("HLA-B15", use_allele_aliases=True)
    off_names = {a.to_string() for a in off.alleles}
    on_names = {a.to_string() for a in on.alleles}
    assert "HLA-B*15:112" in off_names
    assert "HLA-B*15:112" in on_names
    assert "HLA-B*15:11:02" not in on_names
    # Direct historical alias input still resolves as before
    assert parse("HLA-B*15112", use_allele_aliases=True).to_string() == "HLA-B*15:11:02"


def test_every_hla_serotype_matches_across_alias_modes():
    parser_off = Parser(use_allele_aliases=False)
    parser_on = Parser(use_allele_aliases=True)
    hla = Species.get("HLA")

    for serotype_name in serotypes["HLA"]:
        direct_off = parser_off.get_serotype(hla, serotype_name)
        direct_on = parser_on.get_serotype(hla, serotype_name)
        assert [a.to_string() for a in direct_on.alleles] == [
            a.to_string() for a in direct_off.alleles
        ], f"get_serotype mismatch for HLA-{serotype_name}"

        parsed_off = parse(
            f"HLA-{serotype_name}",
            required_result_types=[Serotype],
            use_allele_aliases=False,
        )
        parsed_on = parse(
            f"HLA-{serotype_name}",
            required_result_types=[Serotype],
            use_allele_aliases=True,
        )
        assert [a.to_string() for a in parsed_on.alleles] == [
            a.to_string() for a in parsed_off.alleles
        ], f"parse mismatch for HLA-{serotype_name}"


def test_deliberate_historical_member_in_bola_serotype_still_resolves():
    """BoLA-A11 deliberately carries legacy BoLA-N*01801 -> BoLA-2*018:01."""
    off = parse("BoLA-A11", use_allele_aliases=False)
    on = parse("BoLA-A11", use_allele_aliases=True)
    assert [a.to_string() for a in off.alleles] == ["BoLA-N*018:01"]
    assert [a.to_string() for a in on.alleles] == ["BoLA-2*018:01"]


def test_find_matching_name_and_parse_alleles_separates_normalization_from_alias_lookup():
    hla = Species.get("HLA")
    bola = Species.get("BoLA")
    parser_on = Parser(use_allele_aliases=True)

    compact_table = NormalizingDictionary.from_dict({"B44": ["B*4402", "B*15112"]})
    _, normalized_members, _ = parser_on.find_matching_name_and_parse_alleles(
        "B44", compact_table, hla, use_allele_aliases=False
    )
    assert [a.to_string() for a in normalized_members] == ["HLA-B*44:02", "HLA-B*15:112"]

    historical_table = NormalizingDictionary.from_dict({"A11": ["N*01801"]})
    _, historical_members, _ = parser_on.find_matching_name_and_parse_alleles(
        "A11", historical_table, bola
    )
    transformed = parser_on.transform_parse_candidates(historical_members)
    assert [a.to_string() for a in transformed] == ["BoLA-2*018:01"]


@pytest.mark.parametrize("species_key", sorted(haplotypes))
def test_shipped_haplotypes_are_consistent_across_alias_modes(species_key):
    parser_off = Parser(use_allele_aliases=False)
    parser_on = Parser(use_allele_aliases=True)
    species = Species.get(species_key)
    for name in haplotypes[species_key]:
        r_off = parser_off.transform_parse_candidate(parser_off.get_haplotype(species, name))
        r_on = parser_on.transform_parse_candidate(parser_on.get_haplotype(species, name))
        assert [a.to_string() for a in r_on.alleles] == [a.to_string() for a in r_off.alleles]


def test_shipped_supertypes_and_heterodimers_are_consistent_across_alias_modes():
    parser_off = Parser(use_allele_aliases=False)
    parser_on = Parser(use_allele_aliases=True)

    for species_key, entries in supertypes.items():
        species = Species.get(species_key)
        for name in entries:
            r_off = parser_off.get_supertype(species, name)
            r_on = parser_on.get_supertype(species, name)
            assert [a.to_string() for a in r_on.alleles] == [a.to_string() for a in r_off.alleles]
            assert r_on.representative == r_off.representative

    for species_key, entries in heterodimers.items():
        species = Species.get(species_key)
        for name in entries:
            assert parser_on.get_heterodimer(species, name) == parser_off.get_heterodimer(
                species, name
            )
