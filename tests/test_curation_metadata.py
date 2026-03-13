from pathlib import Path

import yaml

from mhcgnomes import Species


def load_underrepresented_taxa_registry():
    registry_path = (
        Path(__file__).parent.parent
        / "mhcgnomes"
        / "data"
        / "underrepresented_taxa_source_registry.yaml"
    )
    with registry_path.open() as fd:
        return yaml.safe_load(fd)


def test_registry_captures_mhcseqs_review_prefixes():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    for prefix in [
        "Acar",
        "Acsc",
        "Getr",
        "Dare",
        "Orni",
        "Paol",
        "Cyse",
        "Epco",
        "Satr",
        "Chpi",
        "Coja",
        "Fuat",
        "Sphu",
        "Spma",
        "Saal",
        "Ritr",
        "Otel",
        "Tyal",
        "Saha",
        "Gaga",
    ]:
        assert prefix in taxa, prefix


def test_runtime_ready_registry_entries_match_species_ontology():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    for prefix in [
        "Acar",
        "Acsc",
        "Getr",
        "Dare",
        "Orni",
        "Paol",
        "Cyse",
        "Epco",
        "Satr",
        "Chpi",
        "Coja",
        "Fuat",
        "Sphu",
        "Spma",
    ]:
        assert taxa[prefix]["capture_status"] == "runtime_ready"
        assert Species.get(prefix) is not None


def test_registry_marks_held_back_strings_as_partial_capture_only():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    assert taxa["Saal"]["capture_status"] == "partial_capture_only"
    assert taxa["Ritr"]["capture_status"] == "partial_capture_only"
    assert taxa["Otel"]["capture_status"] == "partial_capture_only"
    assert taxa["Tyal"]["capture_status"] == "partial_capture_only"
    assert taxa["Saha"]["capture_status"] == "partial_capture_only"
    assert taxa["Gaga"]["capture_status"] == "partial_capture_only"
    assert "Getr-MHC" in " ".join(taxa["Getr"]["ambiguities"])
    assert "Coja-II-13" in " ".join(taxa["Coja"]["ambiguities"] + taxa["Coja"]["blocked_on"])


def test_registry_tracks_followup_for_runtime_added_coja_ddb1():
    coja = load_underrepresented_taxa_registry()["taxa"]["Coja"]
    assert "DDB1" in coja["canonical_gene_candidates"]
    assert "Coja-DDB1" in " ".join(coja["ambiguities"] + coja["blocked_on"] + [coja["notes"]])
