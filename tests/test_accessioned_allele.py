"""Tests for explicit accession-backed MHC allele identifiers (#309)."""

import pytest

import mhcgnomes
from mhcgnomes import (
    AccessionedAllele,
    Gene,
    ParseError,
    Species,
    dataframe_from_string_list,
    infer_mhc_class,
    parse,
    parse_gene_class,
)


@pytest.mark.parametrize(
    "raw, expected_species, expected_gene, expected_source, expected_acc, expected_class, expected_str",
    [
        (
            "AnasPlatyrhynchos-UAA*uniprot:Q6I7L2",
            "Anas platyrhynchos",
            "UAA",
            "uniprot",
            "Q6I7L2",
            "Ia",
            "AnasPlatyrhynchos-UAA*uniprot:Q6I7L2",
        ),
        (
            "GallusGallus-BF*uniprot:Q95154",
            "Gallus gallus",
            "BF",
            "uniprot",
            "Q95154",
            "Ia",
            "Gaga-BF*uniprot:Q95154",
        ),
        (
            "CtenopharyngodonIdella-UAA*uniprot:Q8JIG4",
            "Ctenopharyngodon idella",
            "UAA",
            "uniprot",
            "Q8JIG4",
            "Ia",
            "CtenopharyngodonIdella-UAA*uniprot:Q8JIG4",
        ),
        (
            "TriakisScyllium-UAA*uniprot:Q9GKI8",
            "Triakis scyllium",
            "UAA",
            "uniprot",
            "Q9GKI8",
            "Ia",
            "TriakisScyllium-UAA*uniprot:Q9GKI8",
        ),
        (
            "MonodelphisDomestica-UT3*uniprot:F7A2B1",
            "Monodelphis domestica",
            "UT3",
            "uniprot",
            "F7A2B1",
            "I",
            "Modo-UT3*uniprot:F7A2B1",
        ),
        (
            "RattusNorvegicus-N3*uniprot:P15978",
            "Rattus norvegicus",
            "N3",
            "uniprot",
            "P15978",
            "I",
            "Rano-N3*uniprot:P15978",
        ),
        (
            "HLA-A*UNIPROT:p04439",
            "Homo sapiens",
            "A",
            "uniprot",
            "P04439",
            "Ia",
            "HLA-A*uniprot:P04439",
        ),
        (
            "HLA-A*uniprot:P04439-2",
            "Homo sapiens",
            "A",
            "uniprot",
            "P04439-2",
            "Ia",
            "HLA-A*uniprot:P04439-2",
        ),
        (
            "AnasPlatyrhynchos-UAA*genbank:GQ411457.1",
            "Anas platyrhynchos",
            "UAA",
            "genbank",
            "GQ411457.1",
            "Ia",
            "AnasPlatyrhynchos-UAA*genbank:GQ411457.1",
        ),
        (
            "MonodelphisDomestica-UT3*refseq:NP_001234.1",
            "Monodelphis domestica",
            "UT3",
            "refseq",
            "NP_001234.1",
            "I",
            "Modo-UT3*refseq:NP_001234.1",
        ),
        (
            "HLA-A*pdb:1hsa_A",
            "Homo sapiens",
            "A",
            "pdb",
            "1HSA_A",
            "Ia",
            "HLA-A*pdb:1HSA_A",
        ),
        (
            "HLA-DRA*uniprot:P01903",
            "Homo sapiens",
            "DRA",
            "uniprot",
            "P01903",
            "IIa",
            "HLA-DRA*uniprot:P01903",
        ),
        (
            "AnasPlatyrhynchos-UAA*uniprot:Q6I7L2 class I",
            "Anas platyrhynchos",
            "UAA",
            "uniprot",
            "Q6I7L2",
            "Ia",
            "AnasPlatyrhynchos-UAA*uniprot:Q6I7L2",
        ),
    ],
)
def test_parse_gene_bearing_accessioned_alleles(
    raw,
    expected_species,
    expected_gene,
    expected_source,
    expected_acc,
    expected_class,
    expected_str,
):
    result = parse(raw)
    assert type(result) is AccessionedAllele
    assert result.species.name == expected_species
    assert result.gene == Gene.get(expected_species, expected_gene)
    assert result.gene_name == expected_gene
    assert result.accession_source == expected_source
    assert result.accession == expected_acc
    assert result.mhc_class == expected_class
    assert result.to_string() == expected_str
    assert result.species_source == "explicit"
    assert result.species_from_input is True
    assert result.is_allele_group is False
    assert result.is_mutant is False
    # Round-trip canonical string
    reparsed = parse(result.to_string())
    assert reparsed == result
    # Atomic under max_allele_fields
    assert result.restrict_allele_fields(2) == result
    assert parse(raw, max_allele_fields=2) == result


@pytest.mark.parametrize(
    "raw, expected_species, expected_source, expected_acc, expected_class, expected_str",
    [
        (
            "SarcophilusHarrisii*uniprot:G3V1L5 class I",
            "Sarcophilus harrisii",
            "uniprot",
            "G3V1L5",
            "I",
            "Saha*uniprot:G3V1L5 class I",
        ),
        (
            "CricetulusGriseus*uniprot:A0A061HWC8 class I",
            "Cricetulus griseus",
            "uniprot",
            "A0A061HWC8",
            "I",
            "CricetulusGriseus*uniprot:A0A061HWC8 class I",
        ),
        (
            "SarcophilusHarrisii*uniprot:G3V1L5",
            "Sarcophilus harrisii",
            "uniprot",
            "G3V1L5",
            None,
            "Saha*uniprot:G3V1L5",
        ),
        (
            "Sarcophilus harrisii*uniprot:G3V1L5 MHC class II",
            "Sarcophilus harrisii",
            "uniprot",
            "G3V1L5",
            "II",
            "Saha*uniprot:G3V1L5 class II",
        ),
        (
            "class I SarcophilusHarrisii*uniprot:G3V1L5",
            "Sarcophilus harrisii",
            "uniprot",
            "G3V1L5",
            "I",
            "Saha*uniprot:G3V1L5 class I",
        ),
        (
            "H-2*uniprot:P01898 class I",
            "Mus musculus",
            "uniprot",
            "P01898",
            "I",
            "H2*uniprot:P01898 class I",
        ),
        (
            "Saha*ena:GQ411457 class I",
            "Sarcophilus harrisii",
            "ena",
            "GQ411457",
            "I",
            "Saha*ena:GQ411457 class I",
        ),
    ],
)
def test_parse_geneless_accessioned_alleles(
    raw,
    expected_species,
    expected_source,
    expected_acc,
    expected_class,
    expected_str,
):
    result = parse(raw)
    assert type(result) is AccessionedAllele
    assert result.species.name == expected_species
    assert result.gene is None
    assert result.gene_name is None
    assert result.accession_source == expected_source
    assert result.accession == expected_acc
    assert result.mhc_class == expected_class
    assert result.is_class1 is (expected_class == "I")
    assert result.is_class2 is (expected_class == "II")
    assert result.is_pseudogene is False
    assert result.pseudogene_status is None
    assert result.to_string() == expected_str
    assert result.species_source == "explicit"
    assert result.species_from_input is True
    # Round-trip
    assert parse(result.to_string()) == result


def test_pseudogene_and_nonclassical_metadata_preserved():
    pseudo = parse("HLA-P*uniprot:P01898")
    assert type(pseudo) is AccessionedAllele
    assert pseudo.is_class1 is True
    assert pseudo.is_pseudogene is True
    assert pseudo.pseudogene_status is True

    mica = parse("HLA-MICA*uniprot:Q29983")
    assert type(mica) is AccessionedAllele
    assert mica.mhc_class == "Ic"
    assert mica.is_class1 is True
    assert mica.is_pseudogene is False

    dra = parse("HLA-DRA*uniprot:P01903")
    assert dra.is_class2 is True
    assert dra.is_class2_alpha is True
    assert dra.class2_chain_type == "alpha"


def test_class_filters_and_species_policies():
    c1 = parse("SarcophilusHarrisii*uniprot:G3V1L5 class I", only_class1=True)
    assert type(c1) is AccessionedAllele
    assert (
        parse("SarcophilusHarrisii*uniprot:G3V1L5 class I", only_class2=True, raise_on_error=False)
        is None
    )
    assert (
        parse("SarcophilusHarrisii*uniprot:G3V1L5", only_class1=True, raise_on_error=False) is None
    )

    # Context-only species prefix rescued with species=
    medaka = parse("Orla-UBA*uniprot:H2LR16", species="Oryzias latipes")
    assert type(medaka) is AccessionedAllele
    assert medaka.species == Species.get("Oryzias latipes")
    assert medaka.gene_name == "UBA"
    assert medaka.accession == "H2LR16"
    assert medaka.species_source == "explicit"

    # Bare gene with default species respects require_explicit_species
    bare_gene = parse("A*uniprot:P04439")
    assert type(bare_gene) is AccessionedAllele
    assert bare_gene.species_source == "default"
    assert parse("A*uniprot:P04439", require_explicit_species=True, raise_on_error=False) is None

    # Ancestor-to-descendant species conversion for gene-less accession
    cow = parse("Bos sp.*uniprot:Q6I7L2 class I", species="Bos taurus")
    assert type(cow) is AccessionedAllele
    assert cow.species == Species.get("Bos taurus")
    assert cow.mhc_class == "I"


@pytest.mark.parametrize(
    "bad_input",
    [
        "uniprot:Q6I7L2",
        "genbank:GQ411457",
        "refseq:NP_001234.1",
        "pdb:1HSA",
        "*uniprot:Q6I7L2",
        "class I *uniprot:Q6I7L2",
        "HLA-A*uniprot:NOT_VALID",
        "HLA-A*uniprot:12345",
        "HLA-A*refseq:Q6I7L2",
        "HLA-A*genbank:abc",
        "HLA-A*pdb:INVALID",
        "HLA-A*uniprot:P04439 class II",
        "HLA-DRA*uniprot:P01903 class I",
        "class I SarcophilusHarrisii*uniprot:G3V1L5 class II",
        "HLA-A*uniprot:P04439 bogus",
        "HLA-A*uniprot:P04439*uniprot:Q6I7L2",
        "AnasPlatyrhynchos-FAKEGENE*uniprot:Q6I7L2",
        "NotASpecies*uniprot:Q6I7L2 class I",
        "HLA-DR*uniprot:P01903",
    ],
)
def test_invalid_accessioned_identifiers_are_rejected(bad_input):
    assert parse(bad_input, raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(bad_input, raise_on_error=True)


def test_parse_gene_class_and_dataframe_integration():
    info_gene = parse_gene_class("AnasPlatyrhynchos-UAA*uniprot:Q6I7L2")
    assert info_gene.species == Species.get("Anas platyrhynchos")
    assert info_gene.gene_name == "UAA"
    assert info_gene.mhc_class == "Ia"
    assert info_gene.chain == "alpha"
    assert info_gene.source == "parsed_allele"

    info_geneless = parse_gene_class("SarcophilusHarrisii*uniprot:G3V1L5 class I")
    assert info_geneless.species == Species.get("Sarcophilus harrisii")
    assert info_geneless.gene_name is None
    assert info_geneless.mhc_class == "I"
    assert info_geneless.chain == "alpha"
    assert infer_mhc_class("SarcophilusHarrisii*uniprot:G3V1L5 class I") == "I"

    df = dataframe_from_string_list(
        [
            "AnasPlatyrhynchos-UAA*uniprot:Q6I7L2",
            "SarcophilusHarrisii*uniprot:G3V1L5 class I",
        ]
    )
    assert list(df["type"]) == ["AccessionedAllele", "AccessionedAllele"]
    assert list(df["accession_source"]) == ["uniprot", "uniprot"]
    assert list(df["accession"]) == ["Q6I7L2", "G3V1L5"]
    assert "AccessionedAllele" in mhcgnomes.__all__
