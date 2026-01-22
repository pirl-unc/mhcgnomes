"""
Tests for parsing HLA/MHC serotypes found in scientific publications.

This test file validates that serotype names commonly found in immunology
literature can be correctly parsed by mhcgnomes.

Sources:

Human HLA disease associations:
  - Blood 2011: "Multiple HLA class I and II associations in classical
    Hodgkin lymphoma" - https://ashpublications.org/blood/article/118/19/5211
    Serotypes: HLA-A1, A2, B7, B8, B37, DR1, DR3, DR10

  - PLOS ONE 2012: "HLA Associations in Classical Hodgkin Lymphoma"
    https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0039986
    Serotypes: A2-B7-DR2 haplotype

  - NCBI Bookshelf: "HLA Association with Autoimmune Diseases"
    https://www.ncbi.nlm.nih.gov/books/NBK459459/
    Serotypes: HLA-B27 (ankylosing spondylitis), DR4 (rheumatoid arthritis)

  - Wikipedia: HLA-B27 - https://en.wikipedia.org/wiki/HLA-B27
    Subtypes: HLA-B*2701 to B*2725

Rhesus macaque (Mamu) SIV studies:
  - Journal of Virology 2006: "The High-Frequency MHC Class I Allele
    Mamu-B*17 Is Associated with Control of SIV Replication"
    https://journals.asm.org/doi/10.1128/jvi.80.10.5074-5077.2006
    Alleles: Mamu-B*17, Mamu-A*01

  - PNAS 2005: "Unparalleled complexity of the MHC class I region"
    https://www.pnas.org/doi/10.1073/pnas.0409084102
    Serotypes: Mamu-A and Mamu-B serotypes defined by cDNA combinations

Chimpanzee (Patr) MHC diversity:
  - PLOS Biology 2015: "Signature Patterns of MHC Diversity in Gombe
    Chimpanzees" - https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002144
    Alleles: Patr-B*22:04, Patr-B*23:05

  - Immunogenetics 2006: "Detailed characterization of the peptide binding
    specificity of five common Patr class I MHC molecules"
    https://link.springer.com/article/10.1007/s00251-006-0131-4
    Alleles: Patr-A*0101, A*0701, A*0901, B*0101, B*2401

Bovine (BoLA) disease studies:
  - PMC 2013: "The Major Histocompatibility Complex in Bovines: A Review"
    https://pmc.ncbi.nlm.nih.gov/articles/PMC3658703/
    Workshop serotypes: w2, w6, w10, w16

  - Journal of Dairy Science 2024: "The DRB3 gene of the bovine MHC"
    https://www.journalofdairyscience.org/article/S0022-0302(24)00989-5
    Alleles: BoLA-DRB3*009:02 (BLV resistance), DRB3*015:01 (susceptibility)
"""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.allele import Allele
from mhcgnomes.serotype import Serotype


class TestHumanHLASerotypesParsing:
    """
    Test parsing of human HLA serotypes from disease association studies.

    These serotypes are commonly referenced in clinical and research literature
    for their associations with autoimmune diseases, cancer susceptibility,
    and transplantation outcomes.
    """

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            # Class I - A locus
            ("HLA-A1", "A1"),
            ("HLA-A2", "A2"),
            ("A1", "A1"),
            ("A2", "A2"),
            # Class I - B locus
            ("HLA-B7", "B7"),
            ("HLA-B8", "B8"),
            ("HLA-B27", "B27"),  # Ankylosing spondylitis association
            ("HLA-B37", "B37"),
            ("B7", "B7"),
            ("B27", "B27"),
            # Class I - C locus
            ("HLA-Cw7", "Cw7"),
            ("HLA-Cw15", "Cw15"),
            ("Cw7", "Cw7"),
            # Class II - DR locus
            ("HLA-DR1", "DR1"),
            ("HLA-DR2", "DR2"),  # Broad serotype
            ("HLA-DR3", "DR3"),  # Broad serotype
            ("HLA-DR4", "DR4"),  # Rheumatoid arthritis association
            ("HLA-DR8", "DR8"),
            ("HLA-DR10", "DR10"),
            ("DR4", "DR4"),
        ],
    )
    def test_common_serotypes_from_disease_studies(self, name, expected_serotype):
        """Serotypes from Hodgkin lymphoma and autoimmune disease studies should parse."""
        result = parse(name)
        assert isinstance(result, Serotype), f"{name} should parse as Serotype"
        assert result.name == expected_serotype

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            # Public epitopes (supertypes)
            ("HLA-Bw4", "Bw4"),
            ("HLA-Bw6", "Bw6"),
            ("Bw4", "Bw4"),
            ("Bw6", "Bw6"),
            # Workshop serotypes (historical names)
            ("HLA-Aw68", "Aw68"),
            ("Aw68", "Aw68"),
        ],
    )
    def test_public_epitopes_and_workshop_names(self, name, expected_serotype):
        """Public epitopes (Bw4/Bw6) and workshop names (Aw68) should parse."""
        result = parse(name)
        assert isinstance(result, Serotype), f"{name} should parse as Serotype"
        assert result.name == expected_serotype
        assert len(result.alleles) > 0, f"{name} should have associated alleles"

    @pytest.mark.parametrize(
        "broad,splits",
        [
            ("A9", ["A23", "A24"]),
            ("DR2", ["DR15", "DR16"]),
            ("DR3", ["DR17", "DR18"]),
        ],
    )
    def test_broad_and_split_serotypes(self, broad, splits):
        """Both broad and split serotypes should parse correctly."""
        # Test broad serotype
        broad_result = parse(f"HLA-{broad}")
        assert isinstance(broad_result, Serotype)
        assert broad_result.name == broad

        # Test split serotypes
        for split in splits:
            split_result = parse(f"HLA-{split}")
            assert isinstance(split_result, Serotype)
            assert split_result.name == split


class TestRhesusMacaqueMamu:
    """
    Test parsing of rhesus macaque (Mamu) MHC names from SIV studies.

    Note: Mamu literature primarily references alleles (e.g., Mamu-B*17)
    rather than serotypes. The library correctly parses these as Allele objects.
    """

    def test_mamu_species_exists(self):
        """Mamu species should be defined."""
        mamu = Species.get("Mamu")
        assert mamu is not None
        assert "rhesus" in mamu.common_name.lower()

    @pytest.mark.parametrize(
        "name",
        [
            "Mamu-A*01",  # Associated with SIV control
            "Mamu-B*17",  # Elite controller allele
            "Mamu-B*08",  # Elite controller allele
        ],
    )
    def test_mamu_alleles_from_siv_studies(self, name):
        """Mamu alleles from SIV vaccine studies should parse as Allele objects."""
        result = parse(name)
        assert isinstance(result, Allele), f"{name} should parse as Allele"
        assert result.species.prefix == "Mamu"

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            ("Mamu-DR2", "DR2"),
            ("Mamu-DR4", "DR4"),
        ],
    )
    def test_mamu_serotypes(self, name, expected_serotype):
        """Mamu DR serotypes should parse correctly."""
        result = parse(name)
        assert isinstance(result, Serotype), f"{name} should parse as Serotype"
        assert result.name == expected_serotype


class TestChimpanzeePatr:
    """
    Test parsing of chimpanzee (Patr) MHC names from diversity studies.

    Sources include studies on MHC diversity in wild chimpanzee populations
    and peptide binding characterization studies.
    """

    def test_patr_species_exists(self):
        """Patr species should be defined."""
        patr = Species.get("Patr")
        assert patr is not None
        assert "chimpanzee" in patr.common_name.lower()

    @pytest.mark.parametrize(
        "name",
        [
            "Patr-A*01:01",  # From peptide binding studies
            "Patr-B*22:04",  # From Gombe population study
            "Patr-B*23:05",  # From Gombe population study
        ],
    )
    def test_patr_alleles_from_diversity_studies(self, name):
        """Patr alleles from population studies should parse as Allele objects."""
        result = parse(name)
        assert isinstance(result, Allele), f"{name} should parse as Allele"
        assert result.species.prefix == "Patr"

    def test_patr_dr_serotypes(self):
        """Patr DR serotypes should parse correctly."""
        result = parse("Patr-DR1")
        assert isinstance(result, Serotype)
        assert result.name == "DR1"


class TestBovineBoLA:
    """
    Test parsing of bovine (BoLA) MHC names from cattle disease studies.

    BoLA-DRB3 alleles are particularly well-studied due to their
    associations with bovine leukemia virus (BLV) resistance.
    """

    def test_bola_species_exists(self):
        """BoLA species should be defined."""
        bola = Species.get("BoLA")
        assert bola is not None

    @pytest.mark.parametrize(
        "name",
        [
            "BoLA-DRB3*009:02",  # BLV resistance
            "BoLA-DRB3*015:01",  # BLV susceptibility
            "BoLA-DRB3*044:01",  # Disease resilience
        ],
    )
    def test_bola_drb3_alleles_from_blv_studies(self, name):
        """BoLA-DRB3 alleles from BLV studies should parse as Allele objects."""
        result = parse(name)
        assert isinstance(result, Allele), f"{name} should parse as Allele"
        assert result.species.prefix == "BoLA"

    def test_bola_a11_serotype(self):
        """BoLA-A11 workshop serotype should parse correctly."""
        result = parse("BoLA-A11")
        assert isinstance(result, Serotype)
        assert result.name == "A11"


class TestEdgeCasesFromPublications:
    """
    Test edge cases and special formats found in scientific literature.
    """

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            # DQ serotypes (diabetes associations)
            ("HLA-DQ2", "DQ2"),
            ("HLA-DQ8", "DQ8"),
            # DP workshop serotypes
            ("HLA-DPw4", "DPw4"),
            # Variant serotypes with lowercase suffix
            ("HLA-B27c", "B27c"),
            ("HLA-DR3d", "DR3d"),
        ],
    )
    def test_special_serotype_formats(self, name, expected_serotype):
        """Special serotype formats from publications should parse."""
        result = parse(name)
        assert isinstance(result, Serotype), f"{name} should parse as Serotype"
        assert result.name == expected_serotype

    def test_case_insensitivity(self):
        """Serotype parsing should be case-insensitive as seen in literature."""
        for name in ["HLA-A2", "hla-a2", "HLA-a2", "Hla-A2"]:
            result = parse(name)
            assert isinstance(result, Serotype), f"{name} should parse"
            assert result.name == "A2"

    def test_b15_broad_serotype_with_many_splits(self):
        """B15 is a broad serotype with many splits - both should parse."""
        # Broad
        b15 = parse("HLA-B15")
        assert isinstance(b15, Serotype)
        assert b15.name == "B15"

        # One of its splits
        b62 = parse("HLA-B62")
        assert isinstance(b62, Serotype)
        assert b62.name == "B62"


class TestAlleleLikeSerotypesPriority:
    """
    Test that serotypes with allele-like names (B3901, A2403, etc.)
    exist but allele interpretation takes priority when parsing.

    These are legitimate WHO serotype designations that happen to
    look like allele names in compact format.
    """

    def test_ambiguous_serotypes_exist_in_data(self):
        """Serotypes like B3901 should exist in the serotype data."""
        human = Species.get("HLA")
        ambiguous = ["B3901", "B3902", "B5102", "B5103", "B4005", "B2708"]
        for name in ambiguous:
            assert name in human.serotypes, f"{name} should be a valid serotype"

    @pytest.mark.parametrize(
        "name",
        [
            "B3901",
            "B*3901",
            "B*39:01",
            "HLA-B3901",
        ],
    )
    def test_allele_like_names_parse_as_alleles(self, name):
        """Names that look like alleles should parse as alleles, not serotypes."""
        result = parse(name)
        assert isinstance(result, Allele), f"{name} should parse as allele"
