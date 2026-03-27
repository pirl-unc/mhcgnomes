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


def active_registry_entries():
    return {
        prefix: entry
        for prefix, entry in load_underrepresented_taxa_registry()["taxa"].items()
        if entry.get("curation_status") == "active"
    }


def entry_sources(entry):
    sources = []
    for key in (
        "taxonomy_sources",
        "structured_sources",
        "literature_sources",
        "representative_annotation_sources",
    ):
        sources.extend(entry.get(key, []))
    return sources


def test_registry_captures_mhcseqs_review_prefixes():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    for prefix in [
        "Acar",
        "Acsc",
        "Cyca",
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
        "Sthi",
        "Sphu",
        "Spma",
        "Saal",
        "Ritr",
        "Otel",
        "Tyal",
        "Saha",
        "Gaga",
        "Phtr",
        "Phco",
        "Zhom",
    ]:
        assert prefix in taxa, prefix


def test_runtime_ready_registry_entries_match_species_ontology():
    for prefix, entry in active_registry_entries().items():
        species = Species.get(prefix)
        assert species is not None, prefix
        assert species.name == entry["scientific_name"], prefix


def test_active_registry_entries_have_source_backed_prefix_provenance():
    for prefix, entry in active_registry_entries().items():
        sources = entry_sources(entry)
        assert sources, prefix
        assert all(source.startswith("http") for source in sources), prefix


def test_registry_marks_held_back_strings_as_sourced():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    assert taxa["Saal"]["curation_status"] == "active"
    assert taxa["Ritr"]["curation_status"] == "blocked"
    assert taxa["Otel"]["curation_status"] == "blocked"
    assert taxa["Saha"]["curation_status"] == "active"
    assert taxa["Phtr"]["curation_status"] == "blocked"
    assert taxa["Phco"]["curation_status"] == "blocked"
    assert taxa["Zhom"]["curation_status"] == "active"
    assert "Getr-MHC" in " ".join(taxa["Getr"]["ambiguities"])
    assert "Coja-II-13" in " ".join(taxa["Coja"]["ambiguities"] + taxa["Coja"]["blocked_on"])
    assert "prefix collides" in " ".join(taxa["Phco"]["ambiguities"])


def test_registry_tracks_runtime_alias_gap_followups():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    cyca_text = " ".join(map(str, taxa["Cyca"]["observed_structure"] + [taxa["Cyca"]["notes"]]))
    tyal_text = " ".join(map(str, taxa["Tyal"]["observed_structure"] + [taxa["Tyal"]["notes"]]))
    assert "UA1" in cyca_text
    assert "MhcTyal-DAB1" in tyal_text
    assert "YFV" in " ".join(taxa["Gaga"]["ambiguities"] + taxa["Gaga"]["blocked_on"])


def test_registry_tracks_followup_for_runtime_added_coja_ddb1():
    coja = load_underrepresented_taxa_registry()["taxa"]["Coja"]
    assert "DDB1" in coja["canonical_gene_candidates"]
    assert "Coja-DDB1" in " ".join(coja["ambiguities"] + coja["blocked_on"] + [coja["notes"]])


def test_registry_tracks_promoted_published_prefixes():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    for prefix, latin in [
        ("Anda", "Andrias davidianus"),
        ("Spau", "Sparus aurata"),
        ("Acda", "Acipenser dabryanus"),
    ]:
        entry = taxa[prefix]
        assert entry["scientific_name"] == latin
        assert entry["curation_status"] == "active"


def test_promoted_prefix_registry_entries_capture_published_and_legacy_forms():
    taxa = load_underrepresented_taxa_registry()["taxa"]
    examples = [
        ("Anda", "AndrDavi", "Anda-MHC"),
        ("Spau", "SparAura", "Spau-DAA"),
        ("Acda", "AcipDabr", "Acda-UAA"),
    ]
    for prefix, legacy_prefix, published_string in examples:
        entry = taxa[prefix]
        observed_text = " ".join(map(str, entry.get("observed_structure", [])))
        assert legacy_prefix in entry["legacy_runtime_prefixes"]
        assert published_string in observed_text
