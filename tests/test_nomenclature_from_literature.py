"""
Tests for MHC nomenclature patterns found in scientific literature and IEDB.

This test file validates parsing of nomenclature patterns commonly encountered
in immunology publications, clinical reports, and databases like IEDB.

Sources and References:
-----------------------
HLA Nomenclature:
    - IPD-IMGT/HLA Database: https://www.ebi.ac.uk/ipd/imgt/hla/
    - HLA Nomenclature: https://hla.alleles.org/
    - History of HLA naming: https://en.wikipedia.org/wiki/History_and_naming_of_human_leukocyte_antigens

HLA Supertypes:
    - Sidney J, et al. "HLA class I supertypes: a revised and updated classification."
      BMC Immunol. 2008;9:1. PMC2245908
      https://pmc.ncbi.nlm.nih.gov/articles/PMC2245908/
    - Sette A, Sidney J. "Nine major HLA class I supertypes account for the vast
      preponderance of HLA-A and -B polymorphism." Immunogenetics. 1999;50:201-12.
      https://pubmed.ncbi.nlm.nih.gov/10602880/

KIR Ligand Groups (C1/C2, Bw4/Bw6):
    - IPD-KIR Ligand Calculator: https://www.ebi.ac.uk/ipd/kir/ligand.html
    - Gwozdowicz S, et al. "KIR specificity and avidity of standard and unusual
      C1, C2, Bw4, Bw6 and A3/11 amino acid motifs." Int J Immunogenet. 2019.
      https://pubmed.ncbi.nlm.nih.gov/31210416/

Non-Human MHC:
    - IPD-MHC Database: https://www.ebi.ac.uk/ipd/mhc/
    - Klein J, et al. "Nomenclature for the major histocompatibility complexes
      of different species." Immunogenetics. 1990;31:217-9.

Disease Associations:
    - HLA-B27 Syndromes: https://www.ncbi.nlm.nih.gov/books/NBK551523/
    - Celiac disease and DQ2/DQ8: PMC3482388

IEDB Data:
    - mhc_ligand_full.csv from https://www.iedb.org/
"""

import pytest

from mhcgnomes import parse
from mhcgnomes.allele import Allele
from mhcgnomes.mhc_class import MhcClass
from mhcgnomes.pair import Pair
from mhcgnomes.serotype import Serotype
from mhcgnomes.species import Species


class TestHumanSerotypesFromIEDB:
    """
    Test human HLA serotypes frequently found in IEDB data.

    IEDB occurrence counts (mhc_ligand_full.csv, top serotype patterns):
        HLA-B27:  211,287
        HLA-A2:   188,953
        HLA-A3:    71,107
        HLA-B35:   63,003
        HLA-A11:   58,725
        HLA-B51:   56,390
        HLA-B7:    53,047
        HLA-A1:    50,436
        HLA-B44:   47,475
        HLA-B15:   44,536
    """

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            # Top 10 serotypes from IEDB
            ("HLA-B27", "B27"),
            ("HLA-A2", "A2"),
            ("HLA-A3", "A3"),
            ("HLA-B35", "B35"),
            ("HLA-A11", "A11"),
            ("HLA-B51", "B51"),
            ("HLA-B7", "B7"),
            ("HLA-A1", "A1"),
            ("HLA-B44", "B44"),
            ("HLA-B15", "B15"),
            # Without prefix
            ("B27", "B27"),
            ("A2", "A2"),
        ],
    )
    def test_top_serotypes_from_iedb(self, name, expected_serotype):
        """Top serotypes from IEDB should parse correctly."""
        result = parse(name)
        assert isinstance(result, Serotype)
        assert result.name == expected_serotype


class TestHumanAllelesFromIEDB:
    """
    Test human HLA alleles frequently found in IEDB data.

    IEDB occurrence counts (top alleles):
        HLA-A*02:01:  39,006
        HLA-B*07:02:  23,792
        HLA-A*01:01:  19,677
        HLA-B*27:05:  17,403
        HLA-A*24:02:  13,742
    """

    @pytest.mark.parametrize(
        "name",
        [
            "HLA-A*02:01",
            "HLA-B*07:02",
            "HLA-A*01:01",
            "HLA-B*27:05",
            "HLA-A*24:02",
            "HLA-B*57:01",
            "HLA-A*03:01",
            "HLA-A*11:01",
            # Without HLA prefix
            "A*02:01",
            "B*07:02",
        ],
    )
    def test_top_alleles_from_iedb(self, name):
        """Top alleles from IEDB should parse as Allele objects."""
        result = parse(name)
        assert isinstance(result, Allele)


class TestClassIIPairsFromIEDB:
    """
    Test Class II alpha/beta pairs from IEDB.

    IEDB occurrence counts:
        HLA-DPA1*01:03/DPB1*04:01:  9,237
        HLA-DPA1*02:02/DPB1*05:01:  6,020
        HLA-DRA*01:01/DRB1*01:01:   5,888
    """

    @pytest.mark.parametrize(
        "name",
        [
            "HLA-DPA1*01:03/DPB1*04:01",
            "HLA-DPA1*02:02/DPB1*05:01",
            "HLA-DRA*01:01/DRB1*01:01",
            "HLA-DQA1*01:02/DQB1*06:02",
            # Without HLA prefix
            "DPA1*01:03/DPB1*04:01",
            "DRA*01:01/DRB1*01:01",
        ],
    )
    def test_class2_pairs_from_iedb(self, name):
        """Class II pairs from IEDB should parse as Pair objects."""
        result = parse(name)
        assert isinstance(result, Pair)


class TestMhcClassFromIEDB:
    """
    Test MHC class nomenclature from IEDB.

    IEDB occurrence counts:
        HLA class I:   96,221
        HLA class II:  32,913
    """

    @pytest.mark.parametrize(
        "name,expected_class",
        [
            ("HLA class I", "I"),
            ("HLA class II", "II"),
            ("MHC class I", "I"),
            ("MHC class II", "II"),
            ("class I", "I"),
            ("class II", "II"),
        ],
    )
    def test_mhc_class_from_iedb(self, name, expected_class):
        """MHC class notation should parse as MhcClass."""
        result = parse(name)
        assert isinstance(result, MhcClass)
        assert result.mhc_class == expected_class


class TestMouseH2FromIEDB:
    """
    Test mouse H-2 nomenclature from IEDB.

    Mouse MHC uses haplotype letters (a, b, d, k, q, s, etc.).

    IEDB occurrence counts:
        H2-Db:   6,257 (class I, b haplotype)
        H2-Kb:   6,082 (class I, b haplotype)
        H2-Kk:   ~600  (class I, k haplotype)
        H2-IAb:  ~100  (class II, b haplotype)
        H2-IAg7: ~100  (class II, NOD mouse)
    """

    @pytest.mark.parametrize(
        "name",
        [
            # Class I
            "H2-Db",
            "H2-Kb",
            "H2-Kd",
            "H2-Kk",
            "H2-Ld",
            "H2-Dd",
            # Class II
            "H2-IAb",
            "H2-IAd",
            "H2-IAk",
            "H2-IEd",
            "H2-IEk",
            # Special: NOD mouse diabetes model
            "H2-IAg7",
            "H2-IEg7",
        ],
    )
    def test_mouse_h2_from_iedb(self, name):
        """Mouse H-2 nomenclature should parse correctly."""
        result = parse(name)
        # H2-D, H2-K, H2-L are class I (parse as Allele)
        # H2-IA, H2-IE are class II (parse as Pair or Haplotype)
        assert result is not None
        assert result.species.common_name.lower() == "mouse"


class TestNonHumanPrimatesFromIEDB:
    """
    Test non-human primate MHC nomenclature.

    Species prefixes:
    - Mamu: Macaca mulatta (rhesus macaque)
    - Patr: Pan troglodytes (chimpanzee)
    - Gogo: Gorilla gorilla (gorilla)

    IEDB occurrence counts (sample):
        Mamu-A1*001:01: 1,708
        Mamu-B*017:04:    717
        Mamu-B*17:        100

    References:
    - IPD-MHC NHP: https://www.ebi.ac.uk/ipd/mhc/group/NHP/
    """

    @pytest.mark.parametrize(
        "name",
        [
            # Rhesus macaque
            "Mamu-A1*001:01",
            "Mamu-A1*011:01",
            "Mamu-B*017:04",
            "Mamu-B*001:01",
            "Mamu-B*17",
            "Mamu-A*01",
            # Chimpanzee
            "Patr-A*01:01",
            "Patr-B*22:04",
        ],
    )
    def test_nhp_alleles_from_iedb(self, name):
        """Non-human primate MHC alleles should parse correctly."""
        result = parse(name)
        assert isinstance(result, Allele)


class TestKIRLigandGroups:
    """
    Test KIR ligand group nomenclature (Bw4, Bw6, C1, C2).

    Bw4 and Bw6 are public epitopes (supertypic specificities) on HLA-B.
    C1 and C2 are KIR ligand groups based on HLA-C polymorphism at position 80.

    References:
    - IPD-KIR Ligand Calculator: https://www.ebi.ac.uk/ipd/kir/ligand.html
    - Gwozdowicz 2019: https://pubmed.ncbi.nlm.nih.gov/31210416/
    """

    @pytest.mark.parametrize(
        "name",
        [
            # Public epitopes (parse as serotypes)
            "Bw4",
            "Bw6",
            "HLA-Bw4",
            "HLA-Bw6",
        ],
    )
    def test_bw4_bw6_public_epitopes(self, name):
        """Bw4 and Bw6 public epitopes should parse as serotypes."""
        result = parse(name)
        assert isinstance(result, Serotype)


class TestHLASupertypes:
    """
    Test HLA supertype nomenclature.

    Supertypes group HLA alleles with similar peptide binding properties.
    Nine major supertypes: A1, A2, A3, A24, B7, B27, B44, B58, B62.

    IEDB occurrence counts:
        B44 supertype: 966
        A2 supertype:  355
        A3 supertype:  221
        A1 supertype:  124
        B7 supertype:   64

    References:
    - Sidney 2008: https://pmc.ncbi.nlm.nih.gov/articles/PMC2245908/
    - Sette & Sidney 1999: https://pubmed.ncbi.nlm.nih.gov/10602880/
    """

    @pytest.mark.parametrize(
        "name",
        [
            "A2 supertype",
            "A3 supertype",
            "B7 supertype",
            "B44 supertype",
            "A1 supertype",
            "A24 supertype",
        ],
    )
    def test_hla_supertypes(self, name):
        """HLA supertype nomenclature should parse as Supertype objects."""
        from mhcgnomes import Supertype

        result = parse(name)
        assert result is not None
        assert isinstance(result, Supertype)


class TestMutantAlleles:
    """
    Test mutant allele nomenclature from IEDB.

    IEDB includes mutant alleles with notation like "HLA-B*27:05 C67S mutant".

    IEDB occurrence counts:
        HLA-B*27:05 C67S mutant:           1,797
        HLA-DRA*01:01/DRB1*01:01 C30S mutant: 888
    """

    @pytest.mark.parametrize(
        "name",
        [
            "HLA-B*27:05 C67S mutant",
            "HLA-A*02:01 Y84A mutant",
        ],
    )
    def test_mutant_alleles(self, name):
        """Mutant allele nomenclature should parse as Allele with mutations."""
        result = parse(name)
        assert isinstance(result, Allele)
        assert len(result.mutations) > 0


class TestWorkshopSerotypes:
    """
    Test workshop (w) serotype nomenclature.

    Workshop serotypes use "w" prefix to indicate provisional designations.
    Common in HLA-C (Cw) and HLA-DP (DPw).
    """

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            ("HLA-Cw7", "Cw7"),
            ("HLA-Cw15", "Cw15"),
            ("Cw7", "Cw7"),
            ("HLA-DPw4", "DPw4"),
            ("HLA-Aw68", "Aw68"),
        ],
    )
    def test_workshop_serotypes(self, name, expected_serotype):
        """Workshop serotypes should parse correctly."""
        result = parse(name)
        assert isinstance(result, Serotype)
        assert result.name == expected_serotype


class TestSerotypeVariants:
    """
    Test serotype variants with letter suffixes.

    Some serotypes have letter suffixes indicating variants (e.g., B27c, DR3d).
    """

    @pytest.mark.parametrize(
        "name,expected_serotype",
        [
            ("HLA-B27c", "B27c"),
            ("HLA-DR3d", "DR3d"),
            ("B27c", "B27c"),
        ],
    )
    def test_serotype_variants(self, name, expected_serotype):
        """Serotype variants with letter suffixes should parse."""
        result = parse(name)
        assert isinstance(result, Serotype)
        assert result.name == expected_serotype


class TestNonClassicalHLA:
    """
    Test non-classical HLA molecules (HLA-E, HLA-F, HLA-G).

    Non-classical MHC-Ib molecules have limited polymorphism and
    specialized immune functions.

    References:
    - Evolution of MHC-G, -E, -F: PMC9352621
    """

    @pytest.mark.parametrize(
        "name",
        [
            "HLA-E*01:01",
            "HLA-F*01:01",
            "HLA-G*01:01",
            "HLA-G*01:04",
        ],
    )
    def test_non_classical_hla_alleles(self, name):
        """Non-classical HLA alleles should parse correctly."""
        result = parse(name)
        assert isinstance(result, Allele)


class TestDogDLA:
    """
    Test dog leukocyte antigen (DLA) nomenclature.

    IEDB occurrence:
        DLA-88*501:01: 1,640
    """

    @pytest.mark.parametrize(
        "name",
        [
            "DLA-88*501:01",
            "DLA-88*502:01",
        ],
    )
    def test_dog_dla_alleles(self, name):
        """Dog DLA alleles should parse correctly."""
        result = parse(name)
        assert isinstance(result, Allele)


class TestCompactAlleleNotation:
    """
    Test compact (no colon) allele notation.

    Older publications often use compact notation like A*0201 instead of A*02:01.
    """

    @pytest.mark.parametrize(
        "compact,standard",
        [
            ("A*0201", "A*02:01"),
            ("B*0702", "B*07:02"),
            ("DRB1*0401", "DRB1*04:01"),
            ("HLA-A*0201", "HLA-A*02:01"),
        ],
    )
    def test_compact_notation(self, compact, standard):
        """Compact notation should parse equivalently to standard notation."""
        compact_result = parse(compact)
        standard_result = parse(standard)

        assert isinstance(compact_result, Allele)
        assert isinstance(standard_result, Allele)
        # Should produce equivalent allele fields
        assert compact_result.allele_fields == standard_result.allele_fields


class TestDiseaseAssociatedAlleles:
    """
    Test disease-associated HLA alleles commonly cited in literature.

    References:
    - HLA-B27 and ankylosing spondylitis: PMID 4405240 (1973 discovery)
    - HLA-DQ2/DQ8 and celiac disease: PMC3482388
    - HLA-B*57:01 and abacavir hypersensitivity
    """

    @pytest.mark.parametrize(
        "name,disease",
        [
            ("HLA-B27", "ankylosing spondylitis"),
            ("HLA-B*27:05", "ankylosing spondylitis (major subtype)"),
            ("HLA-DQ2", "celiac disease"),
            ("HLA-DQ8", "celiac disease"),
            ("HLA-B*57:01", "abacavir hypersensitivity"),
            ("HLA-DR4", "rheumatoid arthritis"),
            ("HLA-DR3", "type 1 diabetes"),
        ],
    )
    def test_disease_associated_alleles(self, name, disease):
        """Disease-associated alleles commonly cited in literature should parse."""
        result = parse(name)
        assert result is not None, f"{name} ({disease}) should parse"


class TestSpeciesExist:
    """Test that key MHC species are defined."""

    @pytest.mark.parametrize(
        "prefix,common_name_contains",
        [
            ("HLA", "human"),
            ("H2", "mouse"),
            ("RT1", "rat"),
            ("Mamu", "rhesus"),
            ("Patr", "chimpanzee"),
            ("BoLA", "cattle"),
            ("SLA", "pig"),
            ("DLA", "canine"),
        ],
    )
    def test_species_defined(self, prefix, common_name_contains):
        """Key MHC species should be defined in mhcgnomes."""
        species = Species.get(prefix)
        assert species is not None, f"Species {prefix} should exist"
        assert common_name_contains in species.common_name.lower()
