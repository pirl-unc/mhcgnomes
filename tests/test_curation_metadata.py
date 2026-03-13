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
    for prefix in ["Acar", "Acsc", "Getr", "Paol", "Cyse", "Epco", "Saal", "Gaga"]:
        assert prefix in taxa, prefix


def test_runtime_ready_registry_entries_match_species_ontology():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    for prefix in ["Acar", "Acsc", "Getr", "Paol", "Cyse", "Epco"]:
        assert taxa[prefix]["capture_status"] == "runtime_ready"
        assert Species.get(prefix) is not None


def test_registry_marks_held_back_strings_as_partial_capture_only():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    assert taxa["Saal"]["capture_status"] == "partial_capture_only"
    assert taxa["Gaga"]["capture_status"] == "partial_capture_only"
    assert "Getr-MHC" in " ".join(taxa["Getr"]["ambiguities"])
