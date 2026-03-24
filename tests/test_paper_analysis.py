import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name, relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


paper_analysis = load_script_module("paper_analysis", "paper/scripts/paper_analysis.py")


def test_infer_species_from_raw_examples():
    assert paper_analysis.infer_species_from_raw("HLA-DPA2") == "Homo sapiens"
    assert paper_analysis.infer_species_from_raw("Acar-DAB*1") == "Acrocephalus arundinaceus"
    assert paper_analysis.infer_species_from_raw("Mygl-DQB*01") == "Myodes glareolus"
    assert paper_analysis.infer_species_from_raw("Nogo-B") is None


def test_major_taxon_for_species_examples():
    assert paper_analysis.major_taxon_for_species("Homo sapiens") == "Human"
    assert paper_analysis.major_taxon_for_species("Macaca fascicularis") == "Non-human primate"
    assert paper_analysis.major_taxon_for_species("Tursiops truncatus") == "Cetacean"
    assert paper_analysis.major_taxon_for_species("Acrocephalus arundinaceus") == "Bird"
    assert paper_analysis.major_taxon_for_species("Salmo salar") == "Fish"
    assert paper_analysis.major_taxon_for_species("Amblyrhynchus cristatus") == "Reptile"
    assert paper_analysis.major_taxon_for_species("Phascolarctos cinereus") == "Other mammal"
    assert paper_analysis.major_taxon_for_species("Myodes glareolus") == "Other mammal"
    assert paper_analysis.major_taxon_for_species("Canis sp.") == "Other mammal"
    assert paper_analysis.major_taxon_for_species("Phocarctos hookeri") == "Other mammal"


def test_classify_failure_mode_examples():
    assert (
        paper_analysis.classify_failure_mode("Acar-DAB*1", "Acrocephalus arundinaceus")
        == "Uncurated species-specific nomenclature"
    )
    assert (
        paper_analysis.classify_failure_mode("HLA-DPA2", "Homo sapiens")
        == "Unsupported locus / gene family"
    )
    assert (
        paper_analysis.classify_failure_mode("RT1-Bad:Token", "Rattus norvegicus")
        == "Formatting / normalization edge case"
    )
    assert paper_analysis.classify_failure_mode("GTPase-GDP", "") == "Residual non-MHC extraction"
