from mhcgnomes import Species, parse
from mhcgnomes.tokenize import tokenize


def test_parse_returns_defensive_copy_from_cache():
    result1 = parse("HLA-A*02:01")
    result2 = parse("HLA-A*02:01")

    assert result1 is not result2

    result1.raw_string = "MUTATED"
    result1.gene.name = "Z"

    result3 = parse("HLA-A*02:01")
    assert result3.raw_string == "HLA-A*02:01"
    assert result3.gene.name == "A"
    assert result3.to_string() == "HLA-A*02:01"


def test_tokenize_returns_defensive_copy_from_cache():
    tokenization1 = tokenize("HLA-A*02:01")
    tokenization2 = tokenize("HLA-A*02:01")

    assert tokenization1 is not tokenization2

    tokenization1.attributes["BAD"] = "1"
    tokenization1.tokens[0].raw_string = "BAD"

    tokenization3 = tokenize("HLA-A*02:01")
    assert "BAD" not in tokenization3.attributes
    assert tokenization3.tokens[0].raw_string != "BAD"
    assert tokenization3.tokens == tokenize("HLA-A*02:01").tokens


def test_species_get_multiple_returns_immutable_cached_collection():
    matches = Species.get_multiple("HLA")

    assert isinstance(matches, tuple)
    assert all(match.prefix == "HLA" for match in matches)

    modified = (*matches, "BAD")
    assert modified[-1] == "BAD"
    assert all(match.prefix == "HLA" for match in Species.get_multiple("HLA"))
