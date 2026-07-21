from pathlib import Path

import pytest

from mhcgnomes.parser import Parser


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("HLA-A02:01", "HLA-A*02:01"),
        ("Patr-A0101", "Patr-A*01:01"),
        ("Mamu-A1:00101", "Mamu-A1*001:01"),
        ("SLA-1:0101", "SLA-1*01:01"),
        ("BoLA-1:00901", "BoLA-1*009:01"),
        ("DLA-8803401", "DLA-88*034:01"),
        ("Eqca-16:00101", "Eqca-16*001:01"),
        ("Gogo-B0101", "Gogo-B*01:01"),
    ],
)
def test_explicit_species_allele_fast_path_is_cross_species(monkeypatch, name, expected):
    parser = Parser()

    def fail_if_general_parser_runs(*args, **kwargs):
        raise AssertionError("eligible allele unexpectedly used the general parser")

    monkeypatch.setattr(parser, "parse_multiple_candidates", fail_if_general_parser_runs)

    result = parser.parse(name)

    assert result.to_string() == expected
    assert result.raw_string == name


@pytest.mark.parametrize(
    "name",
    [
        "A*02:01",
        "HLA-A2",
        "BoLA-HD6",
        "H-2-Db",
        "Gaga-B11",
        "Gaga-BF19",
        "BoLA-DRA-DRB31501",
        "HLA-DRA*01:01/DRB1*03:01",
        "Caja-PS*02:01",
    ],
)
def test_fast_path_defers_unprefixed_non_allele_and_complex_names(name):
    assert Parser()._parse_explicit_species_allele_candidates(name) == []


def test_fast_path_matches_general_parser_for_checked_in_netmhcpan_inventory():
    inventory_path = Path(__file__).parents[1] / "evaluation" / "netmhcpan-4.1-alleles.txt"
    with inventory_path.open() as inventory_file:
        names = [line.split("\t", 1)[0].strip() for line in inventory_file if line.strip()]

    fast_parser = Parser()
    general_parser = Parser()
    general_parser._parse_explicit_species_allele_candidates = lambda name: []

    fast_results = [fast_parser.parse(name) for name in names]
    general_results = [general_parser.parse(name) for name in names]

    assert len(names) == 11_114
    assert fast_results == general_results
    assert [result.to_string() for result in fast_results] == [
        result.to_string() for result in general_results
    ]
