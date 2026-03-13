from dataclasses import FrozenInstanceError

import pytest

from mhcgnomes import Allele, Gene, Species, parse
from mhcgnomes.token import Token
from mhcgnomes.tokenize import TokenizationResult, tokenize


def test_parsed_results_round_trip_through_dict_and_copy():
    allele = parse("HLA-A*02:01 N80I mutant")

    restored = Allele.from_dict(allele.to_dict())
    assert restored == allele
    assert restored.to_string() == allele.to_string()

    updated = allele.copy(raw_string="updated")
    assert updated == allele
    assert updated.raw_string == "updated"
    assert allele.raw_string == "HLA-A*02:01 N80I mutant"


def test_species_round_trips_to_singleton_from_dict():
    species = Species.get("HLA")
    restored = Species.from_dict({"name": species.name, "mhc_prefix": species.prefix})
    assert restored is species


def test_species_ontology_is_read_only_but_copyable():
    species = Species.get("HLA")

    with pytest.raises(TypeError):
        species.gene_aliases["BAD"] = "A"

    mutable_copy = species.gene_aliases.copy()
    mutable_copy["BAD"] = "A"
    assert mutable_copy["BAD"] == "A"
    assert species.find_matching_gene_name("BAD") is None


def test_species_serotype_lists_stay_list_like_but_are_read_only():
    species = Species.get("HLA")
    alleles = species.serotypes["Aw68"]

    assert isinstance(alleles, list)
    with pytest.raises(TypeError):
        alleles.append("A*9999")


def test_token_helpers_round_trip():
    token = Token("class-1", "class I")
    restored = Token.from_dict(token.to_dict())
    assert restored == token
    assert restored.raw_string == token.raw_string


def test_tokenization_result_round_trips_through_helpers():
    tokenization = tokenize("HLA-A*02:01 OS=Homo sapiens")
    restored = TokenizationResult.from_dict(tokenization.to_dict())

    assert restored.tokens == tokenization.tokens
    assert restored.ignored_tokens == tokenization.ignored_tokens
    assert dict(restored.attributes) == dict(tokenization.attributes)
    assert restored.raw_string == tokenization.raw_string
    assert restored.trimmed_string == tokenization.trimmed_string


def test_direct_mutation_of_constructed_gene_raises():
    gene = Gene.get("HLA", "A")
    with pytest.raises(FrozenInstanceError):
        gene.name = "B"
