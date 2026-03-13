from dataclasses import FrozenInstanceError

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.tokenize import tokenize


def test_parse_returns_immutable_cached_result():
    result1 = parse("HLA-A*02:01")
    result2 = parse("HLA-A*02:01")

    assert result1 is result2

    with pytest.raises(FrozenInstanceError):
        result1.raw_string = "MUTATED"
    with pytest.raises(FrozenInstanceError):
        result1.gene.name = "Z"

    result3 = parse("HLA-A*02:01")
    assert result3.raw_string == "HLA-A*02:01"
    assert result3.gene.name == "A"
    assert result3.to_string() == "HLA-A*02:01"


def test_tokenize_returns_immutable_cached_result():
    tokenization1 = tokenize("HLA-A*02:01")
    tokenization2 = tokenize("HLA-A*02:01")

    assert tokenization1 is tokenization2

    with pytest.raises(TypeError):
        tokenization1.attributes["BAD"] = "1"
    with pytest.raises(FrozenInstanceError):
        tokenization1.tokens[0].raw_string = "BAD"

    tokenization3 = tokenize("HLA-A*02:01")
    assert "BAD" not in tokenization3.attributes
    assert tokenization3.tokens[0].raw_string != "BAD"
    assert tokenization3.tokens == tokenize("HLA-A*02:01").tokens


def test_species_get_multiple_returns_immutable_cached_collection():
    matches = Species.get_multiple("HLA")

    assert isinstance(matches, tuple)
    assert all(match.prefix == "HLA" for match in matches)
    with pytest.raises(TypeError):
        matches[0].gene_names.add("BAD")

    modified = (*matches, "BAD")
    assert modified[-1] == "BAD"
    assert all(match.prefix == "HLA" for match in Species.get_multiple("HLA"))
