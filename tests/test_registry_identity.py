"""Accession identity, source spelling, and parser-policy guarantees for the full inventory."""

import json
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace

import pytest

from mhcgnomes import (
    Allele,
    AlleleWithoutGene,
    Gene,
    ParseError,
    Parser,
    dataframe_from_string_list,
    get_registry_identities,
    get_registry_identity,
    parse,
    registry_identities,
)
from mhcgnomes.registry_identity import build_registry_index

IDENTITIES = tuple(registry_identities().values())
SPELLINGS = [
    (identity, name)
    for identity in IDENTITIES
    if identity.status == "abandoned"
    for name in (identity.accession, identity.identifier, *identity.names)
]


@pytest.mark.parametrize("identity,name", SPELLINGS, ids=[name for _, name in SPELLINGS])
def test_every_recorded_name_and_accession_has_source_backed_candidates(identity, name):
    result = parse(name, use_allele_aliases=True, require_explicit_species=True)
    expected = parse(identity.canonical_name)
    assert result == expected
    assert hash(result) == hash(expected)
    assert result.raw_string == name
    candidates = get_registry_identities(name)
    assert result.registry_identities == candidates
    assert identity in candidates
    if len(candidates) == 1:
        assert result.registry_identity == identity
        assert result.registry_id == identity.identifier
        assert result.to_record()["registry_id"] == identity.identifier
        assert result.to_record()["registry_status"] == "abandoned"
    else:
        assert result.registry_identity is None
        assert "registry_status" not in result.to_record()
    assert result.to_string() == identity.canonical_name
    assert result.species.name == identity.species_name
    assert result.species_source == "explicit"
    assert identity.status == "abandoned"
    assert parse(result.to_string(), use_allele_aliases=True) == result


@pytest.mark.parametrize("identity", IDENTITIES, ids=lambda r: r.accession)
def test_accessions_do_not_need_aliases_and_apply_parser_policies(identity):
    expected = parse(identity.canonical_name)
    for name in (identity.accession, identity.identifier, identity.canonical_name):
        result = parse(name, default_species="H2", require_explicit_species=True)
        assert result == expected
        assert identity in result.registry_identities
        if name != identity.canonical_name:
            assert result.registry_identity is identity
        assert parse(name, species=identity.species_name) == expected
        assert parse(name, species="Homo sapiens", raise_on_error=False) is None
        wrong_class = {
            "only_class1": identity.mhc_class == "II",
            "only_class2": identity.mhc_class == "I",
        }
        assert parse(name, **wrong_class, raise_on_error=False) is None
        assert parse(name, required_result_types=[Gene], raise_on_error=False) is None
        assert parse(name, required_result_types=[type(expected)]) == expected
        assert parse(name, preferred_result_types=[Gene]) == expected


def test_historical_resolution_is_opt_in_and_resolution_loss_drops_identity():
    assert get_registry_identity("Mamu-AG*01").accession == "NHP00355"
    assert get_registry_identity("Mamu-AG*01", include_aliases=False) is None
    partial = parse("Mamu-AG*01")
    assert partial.to_string() == "Mamu-AG*01"
    assert partial.is_allele_group
    assert partial.registry_identity is None
    assert parse("Mamu-AG*01", use_allele_aliases=True).registry_id == "IPD-MHC:NHP00355"
    for identity in IDENTITIES:
        result = parse(identity.accession, max_allele_fields=1)
        assert result.registry_id is None
        assert parse(identity.accession, max_allele_fields=4).registry_id == identity.identifier
    mutant = parse("Mamu-AG*01:01 N80I mutant")
    assert mutant.is_mutant
    assert mutant.registry_identity is None
    assert "registry_id" not in mutant.to_record()
    assert parse("Mamu-B17", use_allele_aliases=True).name == "B17"


def test_unestablished_dp1_designation_keeps_its_own_identity():
    result = parse("NHP10764")
    assert isinstance(result, AlleleWithoutGene)
    assert result.to_string() == "Paha-DP1*06:01"
    assert result.mhc_class == "II"
    assert result.registry_id == "IPD-MHC:NHP10764"
    assert Gene.get("Paha", "DP1") is None
    assert result != parse("Paha-DPB1*06:01", raise_on_error=False)
    assert parse("NHP10764", required_result_types=[Allele], raise_on_error=False) is None
    assert parse("NHP10764", infer_class2_pairing=True) == result
    assert parse("Paha-DP1*99:99", raise_on_error=False) is None


def test_retained_record_name_wins_over_another_accessions_history():
    # NHP04329's history also contains this designation; no source asserts that
    # the accessions are equal. Evidence and follow-up: issue #250.
    for enabled in (False, True):
        result = parse("Mafa-B*051:06:03", use_allele_aliases=enabled)
        assert result.registry_id == "IPD-MHC:NHP11987"
        assert result.to_string() == "Mafa-B*051:06:03"
        assert result != parse("Mafa-B*051:26", use_allele_aliases=enabled)


def test_registry_lookup_and_public_index_contract():
    identity = get_registry_identity("  ipd-mhc:nhp00355  ")
    assert identity is get_registry_identity("mamu-ag*01:01")
    assert len(registry_identities()) == 78
    assert sum(r.status == "abandoned" for r in IDENTITIES) == 76
    assert len(set(IDENTITIES)) == 78
    assert identity == replace(identity, status="changed metadata")
    assert hash(identity) == hash(replace(identity, status="changed metadata"))
    assert identity != identity.identifier
    with pytest.raises(FrozenInstanceError):
        identity.status = "public"
    with pytest.raises(TypeError):
        registry_identities()[identity.identifier] = identity
    aliases = list(identity.aliases)
    copied = replace(identity, aliases=aliases)
    aliases.append("not an alias")
    assert copied.aliases == identity.aliases
    index = build_registry_index([identity])
    assert index["mamu-ag*01"] == (identity,)
    with pytest.raises(TypeError):
        index["other"] = identity
    assert "mamu-ag*01" not in build_registry_index([identity], include_aliases=False)
    other = replace(identity, accession="NHP99999")
    for rows in ([identity, other], [other, identity]):
        index = build_registry_index(rows)
        assert index["mamu-ag*01:01"] == (identity, other)
        assert index["nhp00355"] == (identity,)
    with pytest.raises(ValueError, match="Duplicate registry identifiers"):
        build_registry_index([identity, identity])
    history = replace(other, canonical_name="Mamu-AG*99:99", aliases=(identity.canonical_name,))
    assert build_registry_index([identity, history])["mamu-ag*01:01"] == (identity,)
    assert get_registry_identity("HLA-A*02:01") is None  # explicitly limited coverage
    assert get_registry_identity("Mamu-AG*0101") is None  # exact source boundaries
    for value in [None, 123]:
        with pytest.raises(TypeError, match="expected str"):
            get_registry_identity(value)


@pytest.mark.parametrize("name", ["NHP99999999", "IPD-MHC:NHP99999999", "IPD-MHC:garbage"])
def test_unknown_accessions_fail_without_heuristic_species_fallback(name):
    assert parse(name, raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(name)


def test_public_registry_parser_building_block():
    parser = Parser()
    assert parser.parse_registry_allele("NHP00355") == parse("Mamu-AG*01:01")
    assert parser.parse_registry_allele("Mamu-AG*01") is None
    assert (
        Parser(use_allele_aliases=True).parse_registry_allele("Mamu-AG*01").registry_id
        == "IPD-MHC:NHP00355"
    )
    assert parser.parse_registry_allele("not a registry name") is None
    with pytest.raises(TypeError):
        parser.parse_registry_allele(None)


def test_dataframe_and_cli_cover_every_spelling_and_keep_status():
    names = [name for _, name in SPELLINGS]
    frame = dataframe_from_string_list(names, use_allele_aliases=True)
    assert frame["input"].tolist() == names
    for row, (_, name) in zip(frame.to_dict("records"), SPELLINGS):
        candidates = get_registry_identities(name)
        if len(candidates) == 1:
            assert row["registry_id"] == candidates[0].identifier
            assert row["registry_status"] == "abandoned"
        else:
            assert row["registry_id_candidates"] == tuple(r.identifier for r in candidates)
    completed = subprocess.run(
        [sys.executable, "-m", "mhcgnomes", "--format", "json", "--use-allele-aliases"],
        input="\n".join(names),
        capture_output=True,
        text=True,
        check=True,
    )
    rows = json.loads(completed.stdout)
    assert [row["input"] for row in rows] == names
    assert [row["normalized"] for row in rows] == frame["normalized"].tolist()
    for row, (identity, name) in zip(rows, SPELLINGS):
        if len(get_registry_identities(name)) == 1:
            assert f"registry_id={identity.identifier}" in row["properties"]
            assert "registry_status=abandoned" in row["properties"]
        else:
            assert "registry_id_candidates=IPD-MHC:NHP04701,IPD-MHC:NHP11988" in row["properties"]
            assert "registry_status=" not in row["properties"]


def test_shared_latest_name_retains_both_accessions_without_claiming_equivalence():
    name = "Mafa-DQA1*01:16:01"
    candidates = get_registry_identities(name)
    assert tuple(r.accession for r in candidates) == ("NHP04701", "NHP11988")
    assert tuple(r.status for r in candidates) == ("public", "abandoned")
    assert get_registry_identity(name) is None
    for enabled in (False, True):
        result = parse(name, use_allele_aliases=enabled)
        assert result.registry_id is None
        assert result.registry_identities == candidates
        assert result.to_record()["registry_id_candidates"] == tuple(
            r.identifier for r in candidates
        )
    for identity in candidates:
        result = parse(identity.accession)
        assert result.registry_identity is identity
        assert result.restrict_allele_fields(2).registry_identity is None
        assert result.copy(allele_fields=("99", "99")).registry_identity is None
        assert result.copy(raw_string="different source").registry_identity is None
    assert candidates[0] != candidates[1]
    assert parse("Mafa-DQA1*01:16", use_allele_aliases=True).registry_id == "IPD-MHC:NHP04701"
    assert parse("Mafa-DQA1*01:16").registry_id is None
    assert parse("NHP04329").registry_id == "IPD-MHC:NHP04329"
    assert get_registry_identity("Mafa-B*051:06:03").accession == "NHP11987"
