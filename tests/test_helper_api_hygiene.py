"""Tests for promoted function_api helpers and helper documentation hygiene (#225)."""

import ast
from pathlib import Path

from mhcgnomes import Species, parse
from mhcgnomes.function_api import (
    build_gene_class_info_from_family,
    build_gene_class_info_from_parsed,
    build_gene_class_info_from_token,
    cached_parser,
    chain_for_species_gene,
    extract_species_and_gene_string,
    reparse_context_only_gene,
    reparse_result_for_species,
    reparse_with_context_only_prefix,
)

from .common import eq_

PACKAGE_DIR = Path(__file__).resolve().parent.parent / "mhcgnomes"
TESTS_DIR = Path(__file__).resolve().parent


def test_promoted_function_api_gene_class_builders():
    parsed = parse("HLA-A*02:01", raise_on_error=True)
    info = build_gene_class_info_from_parsed(parsed, "HLA-A*02:01")
    assert info is not None
    eq_(info.gene_name, "A")
    eq_(info.mhc_class, "Ia")
    eq_(info.chain, "alpha")
    eq_(info.source, "parsed_allele")

    human = Species.get("Homo sapiens")
    eq_(chain_for_species_gene(human, "DRB1", "IIa"), "beta")
    eq_(chain_for_species_gene(human, "A", "Ia"), "alpha")
    eq_(chain_for_species_gene(human, "TAP1", "other"), None)

    family_info = build_gene_class_info_from_family(human, "TAP", "HLA-TAP")
    assert family_info is not None
    eq_(family_info.source, "ontology_family")
    eq_(family_info.non_mhc, True)

    token_info = build_gene_class_info_from_token(human, "DRB1", "HLA-DRB1")
    assert token_info is not None
    eq_(token_info.source, "canonical_gene")
    eq_(token_info.chain, "beta")

    sp, gene_str, err = extract_species_and_gene_string("HLA-A*02:01", cached_parser(), None)
    eq_(sp, human)
    eq_(gene_str, "-A*02:01")
    assert err is None


def test_promoted_function_api_reparse_helpers():
    parser = cached_parser()

    sla_allele = parse("SLA-1*04:01", raise_on_error=True)
    pig = Species.get("Sus scrofa")
    reparsed = reparse_result_for_species(
        parser=parser,
        result=sla_allele,
        expected_species=pig,
        infer_class2_pairing=False,
        required_result_types=(),
        preferred_result_types=(),
        only_class1=False,
        only_class2=False,
        max_allele_fields=None,
    )
    assert reparsed is not None
    eq_(reparsed.species, pig)
    eq_(reparsed.species_source, "explicit")

    medaka = Species.get("Oryzias latipes")
    rescued_prefix = reparse_with_context_only_prefix(
        parser=parser,
        raw_string="Orla-UBA",
        expected_species=medaka,
        infer_class2_pairing=False,
        required_result_types=(),
        preferred_result_types=(),
        only_class1=False,
        only_class2=False,
        max_allele_fields=None,
    )
    assert rescued_prefix is not None
    eq_(rescued_prefix.to_string(), "OryzLati-UBA")
    eq_(rescued_prefix.species_source, "explicit")

    human = Species.get("Homo sapiens")
    rescued_gene = reparse_context_only_gene(
        parser=parser,
        raw_string="N",
        expected_species=human,
        infer_class2_pairing=False,
        required_result_types=(),
        preferred_result_types=(),
        only_class1=False,
        only_class2=False,
        max_allele_fields=None,
    )
    assert rescued_gene is not None
    eq_(rescued_gene.to_string(), "HLA-N")
    eq_(rescued_gene.species_source, "default")


def test_every_private_helper_in_package_is_documented():
    undocumented = []
    for path in sorted(PACKAGE_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if (
                isinstance(node, ast.FunctionDef)
                and node.name.startswith("_")
                and not node.name.startswith("__")
                and not ast.get_docstring(node)
            ):
                undocumented.append(f"{path.name}:{node.lineno} {node.name}")
            elif isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if (
                        isinstance(sub, ast.FunctionDef)
                        and sub.name.startswith("_")
                        and not sub.name.startswith("__")
                        and not ast.get_docstring(sub)
                    ):
                        undocumented.append(f"{path.name}:{sub.lineno} {node.name}.{sub.name}")
    assert undocumented == [], f"Undocumented private helpers: {undocumented}"


def test_no_test_imports_private_helpers_from_mhcgnomes():
    private_imports = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("mhcgnomes")
            ):
                for alias in node.names:
                    if alias.name.startswith("_") and not alias.name.startswith("__"):
                        private_imports.append(
                            f"{path.name}:{node.lineno} from {node.module} import {alias.name}"
                        )
    assert private_imports == [], f"Tests importing private mhcgnomes helpers: {private_imports}"
