"""Broad typing expands candidates without becoming a specific split (#196)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from mhcgnomes import Serotype, Species, dataframe_from_string_list, parse
from mhcgnomes.serotype_hierarchy import expand_serotype_memberships, serotype_descendants

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generate_serotype_hierarchy import parse_serotype_relationships

DATA = Path(__file__).resolve().parents[1] / "mhcgnomes/data"
GRAPH = yaml.safe_load((DATA / "serotype_splits.yaml").read_text())["HLA"]


def test_b12_includes_b44_b45_and_preserves_the_reported_type():
    for aliases in (False, True):
        result = parse("HLA-B12", use_allele_aliases=aliases)
        assert isinstance(result, Serotype)
        assert result.name == "B12"
        assert result.raw_string == "HLA-B12"
        members = {allele.to_string() for allele in result.alleles}
        expected = {
            parse(name, use_allele_aliases=aliases).to_string()
            for name in ("HLA-B*4402", "HLA-B*4415", "HLA-B*4501")
        }
        assert expected <= members
        for split in ("B44", "B45"):
            assert set(parse("HLA-" + split, use_allele_aliases=aliases).alleles) <= set(
                result.alleles
            )
        assert parse("HLA-B12", collapse_singleton_serotypes=True) == result
        assert result.copy(raw_string="B12").name == "B12"
        assert result.to_record()["serotype"] == "HLA-B12"
    assert dataframe_from_string_list(["HLA-B12"])["normalized"].tolist() == ["HLA-B12"]


def test_direct_assignments_remain_separate_and_reverse_candidates_include_broad():
    human = Species.get("HLA")
    assert list(human.direct_serotypes["B12"]) == ["B*4415"]
    assert "B*4402" not in human.direct_serotypes["B12"]
    reverse = {name for name, members in human.serotypes.items() if "B*4402" in members}
    assert {"B44", "B12"} <= reverse
    original = yaml.safe_load((DATA / "serotypes.yaml").read_text())["HLA"]
    assert dict(human.direct_serotypes) == original
    with pytest.raises(TypeError):
        human.direct_serotypes["B12"].append("B*4501")


def test_cli_keeps_the_reported_broad_label():
    completed = subprocess.run(
        [sys.executable, "-m", "mhcgnomes", "--format", "json", "HLA-B12"],
        text=True,
        capture_output=True,
        check=True,
    )
    row = json.loads(completed.stdout)[0]
    assert row["input"] == row["normalized"] == "HLA-B12"
    assert row["type"] == "Serotype"


def test_other_species_keep_their_direct_memberships():
    from mhcgnomes.data import direct_serotypes, serotypes

    for prefix, direct in direct_serotypes.items():
        if prefix != "HLA":
            assert dict(serotypes[prefix]) == dict(direct)


def test_every_shipped_relationship_has_consistent_transitive_candidates():
    human = Species.get("HLA")
    assert len(GRAPH) == 23
    assert sum(map(len, GRAPH.values())) == 57
    # These are cellular specificities: no molecular assignments in this curation.
    absent = {
        name
        for broad, splits in GRAPH.items()
        for name in [broad, *splits]
        if name not in human.serotypes
    }
    assert absent == {"Dw6", "Dw7", "Dw11", "Dw17", "Dw18", "Dw19"}
    for broad, descendants in serotype_descendants(GRAPH).items():
        if broad not in human.serotypes:
            continue
        broad_result = parse("HLA-" + broad)
        assert isinstance(broad_result, Serotype)
        assert broad_result.name == broad
        for split in descendants:
            assert set(human.serotypes[split]) <= set(human.serotypes[broad])
            assert set(parse("HLA-" + split).alleles) <= set(broad_result.alleles)
    assert GRAPH["B15"] == ["B62", "B63", "B75", "B76", "B77"]
    assert GRAPH["B70"] == ["B71", "B72"]


def test_multilevel_expansion_is_upward_deterministic_and_nonmutating():
    direct = {"B1": ["a"], "B2": ["b"], "B3": ["c", "b"], "B4": ["d"]}
    graph = {"B1": ["B2"], "B2": ["B3"]}
    expected = {"B1": ["a", "b", "c"], "B2": ["b", "c"], "B3": ["c", "b"], "B4": ["d"]}
    assert expand_serotype_memberships(direct, graph) == expected
    assert (
        expand_serotype_memberships(
            dict(reversed(list(direct.items()))), dict(reversed(list(graph.items())))
        )
        == expected
    )
    assert direct["B1"] == ["a"]
    assert graph["B1"] == ["B2"]
    assert expand_serotype_memberships({"B1": ["a"]}, graph) == {"B1": ["a"]}


@pytest.mark.parametrize(
    "graph",
    [
        {"B1": ["B1"]},
        {"B1": ["B2"], "B2": ["B1"]},
        {"B1": ["B3"], "B2": ["B3"]},
        {"B1": ["B2", "B2"]},
        {"B1": ["A2"]},
        {"B1": "B2"},
        {"bad": ["B2"]},
    ],
)
def test_invalid_graphs_fail_even_without_direct_members(graph):
    with pytest.raises(ValueError):
        expand_serotype_memberships({}, graph)


def test_wmda_parser_uses_splits_not_associated_antigens():
    assert parse_serotype_relationships("# header\nB;12;44/45;\nB;44;;4402/4404\n") == {
        "B12": ["B44", "B45"]
    }
    assert parse_serotype_relationships("A;2;;0201/0202\n") == {}


@pytest.mark.parametrize(
    "text",
    [
        "B;12;44/45",
        "B;12;44;\nB;12;45;",
        "B;12;44//45;",
        "B;12;44;\nB;44;12;",
        "B;12;44;\nB;13;44;",
    ],
)
def test_malformed_wmda_sources_fail(text):
    with pytest.raises(ValueError):
        parse_serotype_relationships(text)
