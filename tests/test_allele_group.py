"""
Allele.is_allele_group: does a parsed name denote an allele group or one allele (#215)?
"""

import importlib.util
from pathlib import Path

import pytest
import yaml

from mhcgnomes import Allele, parse
from mhcgnomes.allele import _single_field_allele_names
from mhcgnomes.data import single_field_alleles


@pytest.mark.parametrize(
    "name, expected",
    [
        # The issue's examples.
        ("HLA-A*02", True),
        ("HLA-DRB1*04", True),
        ("HLA-A*02:01", False),
        ("H2-Kb", False),
        ("RT1-Aa", False),
        # IPD-MHC lineages are groups too.
        ("Mamu-A1*001", True),
        ("DLA-88*001", True),
        ("Mamu-DRB*W003", True),
        # Low-resolution SLA types name every allele in the group.
        ("SLA-1*15XX", True),
        # Provisional single-allele names are not groups.
        ("SLA-1*es11", False),
        # Complete registry alleles with one numeric field.
        ("HLA-MICA*001", False),
        ("Papa-B*03", False),
        ("Mamu-G*05", False),
        # ... but other one-field names of the same genes are still groups.
        ("HLA-MICA*008", True),
        ("Mamu-G*04", True),
        # G and P groups fix the peptide-binding domain.
        ("HLA-A*02:01:01G", False),
        ("HLA-A*02:01P", False),
        ("HLA-A*02:01:01:01", False),
    ],
)
def test_is_allele_group(name, expected):
    allele = parse(name)
    assert type(allele) is Allele
    assert allele.is_allele_group is expected


@pytest.mark.parametrize(
    "name, resolved",
    [
        ("Mamu-A01", "Mamu-A1*001:01"),
        ("Mamu-B08", "Mamu-B*008:01"),
        ("Mamu-A26", "Mamu-A1*026:01"),
    ],
)
def test_netmhc_short_names_are_single_alleles_once_resolved(name, resolved):
    allele = parse(name, use_allele_aliases=True)
    assert allele.to_string() == resolved
    assert allele.is_allele_group is False


def test_unresolved_old_name_reads_as_a_group():
    # Without alias resolution Mamu-A01 stays Mamu-A*01, a one-field name.
    # Reporting it as a group is the safe direction: a caller that needs one
    # molecule refuses it rather than accepting a group.
    allele = parse("Mamu-A01")
    assert allele.to_string() == "Mamu-A*01"
    assert allele.is_allele_group is True


def _registry_names():
    for prefix, genes in single_field_alleles.items():
        for gene, fields in genes.items():
            for field in fields:
                yield f"{prefix}-{gene}*{field}"


def test_every_registry_single_field_name_is_one_allele():
    checked = 0
    for name in _registry_names():
        allele = parse(name)
        assert allele.is_allele_group is False, name
        checked += 1
    assert checked > 150


def test_every_registry_entry_resolves_to_a_species_and_gene():
    entries = sum(len(genes) for genes in single_field_alleles.values())
    assert len(_single_field_allele_names()) == entries


def _load_generator():
    path = Path(__file__).resolve().parent.parent / "scripts" / "generate_single_field_alleles.py"
    spec = importlib.util.spec_from_file_location("generate_single_field_alleles", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generator_keeps_only_complete_one_field_numeric_names():
    generator = _load_generator()
    table = generator.single_field_alleles(
        [
            ("HLA", "MICA*001"),
            ("HLA", "MICA*002N"),  # an expression suffix does not add a field
            ("HLA", "MICA*008:01:01"),  # two fields
            ("Mamu", "DRB*W003"),  # W prefix: still numeric
            ("Rano", "A1*b"),  # letters: never read as a group
            ("Papa", "B*03"),
        ]
    )
    assert table == {
        "HLA": {"MICA": ["001", "002"]},
        "Mamu": {"DRB": ["W003"]},
        "Papa": {"B": ["03"]},
    }
    text = generator.to_yaml(table)
    assert yaml.safe_load(text) == table
    assert '"001"' in text
