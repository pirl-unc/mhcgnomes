"""Ensure mhcgnomes/data/ ships only runtime-loaded data files (#221)."""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "mhcgnomes" / "data"

RUNTIME_DATA_FILES = {
    "allele_aliases.yaml",
    "current_allele_names.yaml",
    "evidenced_prefix_aliases.yaml",
    "external_sources.json",
    "first_allele_field_widths.yaml",
    "gene_aliases.yaml",
    "haplotypes.yaml",
    "heterodimers.yaml",
    "ipd_record_annotations.json",
    "known_alleles.yaml",
    "registry_allele_identities.json",
    "serotype_splits.yaml",
    "serotypes.yaml",
    "single_field_alleles.yaml",
    "species.yaml",
    "supertypes.yaml",
    "underrepresented_taxa_source_registry.yaml",
}


def test_package_data_directory_contains_only_runtime_files():
    actual = {path.name for path in DATA_DIR.iterdir() if path.is_file()}
    assert actual == RUNTIME_DATA_FILES


def test_pyproject_package_data_matches_runtime_files():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = set(pyproject["tool"]["setuptools"]["package-data"]["mhcgnomes"])
    expected = {f"data/{name}" for name in RUNTIME_DATA_FILES}
    assert declared == expected
