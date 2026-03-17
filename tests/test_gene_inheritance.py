"""
Tests for taxonomic gene inheritance and cross-taxon leak prevention.

Species inherit genes from their parent node (e.g., salmonids from
Salmonidae sp.). Common genes (DMA, TAP1, B2M) are accepted universally.
Taxon-specific genes must NOT leak across boundaries.
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# Salmonid inheritance
# ---------------------------------------------------------------------------


class TestSalmonidInheritance:
    """Salmonid species inherit UBA, DAA, DAB from Salmonidae sp."""

    def test_salmonid_parent_has_genes(self):
        sp = Species.get("Salmonidae sp.")
        assert sp is not None
        assert sp.find_matching_gene_name("UBA") is not None
        assert sp.find_matching_gene_name("DAA") is not None
        assert sp.find_matching_gene_name("DAB") is not None

    def test_rainbow_trout_inherits_uba(self):
        eq_(parse("Onmy-UBA", raise_on_error=True).species.prefix, "Onmy")

    def test_atlantic_salmon_inherits_daa(self):
        eq_(parse("Sasa-DAA", raise_on_error=True).species.prefix, "Sasa")

    def test_brown_trout_inherits_uba(self):
        eq_(parse("Satr-UBA", raise_on_error=True).species.prefix, "Satr")

    def test_brown_trout_inherits_daa(self):
        """Brown trout previously had DAA only as a species-specific gene.
        Now it inherits from the salmonid parent."""
        eq_(parse("Satr-DAA", raise_on_error=True).species.prefix, "Satr")

    def test_arctic_char_inherits_plus_own_genes(self):
        """Arctic char inherits salmonid genes AND has UEA, UGA of its own."""
        sp = Species.get("Saal")
        assert sp.find_matching_gene_name("UBA") is not None  # inherited
        assert sp.find_matching_gene_name("UEA") is not None  # own
        assert sp.find_matching_gene_name("UGA") is not None  # own
        assert sp.find_matching_gene_name("DAB") is not None  # inherited


# ---------------------------------------------------------------------------
# Common genes (truly universal)
# ---------------------------------------------------------------------------


class TestGnathostomataRootInheritance:
    """DMA, DMB, TAP1, TAP2, TAPBP, B2M inherited from Gnathostomata root."""

    @pytest.mark.parametrize(
        "latin",
        [
            "Chelonia mydas",  # turtle → Testudines → Gnathostomata
            "Struthio camelus",  # ratite → Gnathostomata (no intermediate)
            "Crocodylus porosus",  # croc → Crocodylia → Gnathostomata
            "Sphenodon punctatus",  # tuatara → Gnathostomata (no intermediate)
        ],
    )
    def test_root_genes_inherited_via_tree(self, latin):
        sp = Species.get(latin)
        assert sp is not None
        for gene in ["DMA", "TAP1"]:
            assert sp.find_matching_gene_name(gene) is not None, (
                f"{latin} should inherit {gene} from Gnathostomata root"
            )

    def test_root_gene_with_default_species(self):
        result = parse("DMA", default_species="Chelonia mydas", raise_on_error=True)
        assert result is not None
        eq_(result.species.name, "Chelonia mydas")


# ---------------------------------------------------------------------------
# Cross-taxon leak prevention
# ---------------------------------------------------------------------------


class TestCrossTaxonLeakPrevention:
    """Taxon-specific genes must NOT be accepted by species from other taxa."""

    def test_human_does_not_get_fish_uaa(self):
        sp = Species.get("HLA")
        assert sp.find_matching_gene_name("UAA") is None

    def test_human_does_not_get_fish_uba(self):
        sp = Species.get("HLA")
        assert sp.find_matching_gene_name("UBA") is None

    def test_human_does_not_get_fish_dab(self):
        sp = Species.get("HLA")
        assert sp.find_matching_gene_name("DAB") is None

    def test_zebrafish_does_not_get_mammal_drb(self):
        sp = Species.get("Dare")
        assert sp.find_matching_gene_name("DRB") is None

    def test_zebrafish_does_not_get_mammal_drb1(self):
        sp = Species.get("Dare")
        assert sp.find_matching_gene_name("DRB1") is None

    def test_chicken_does_not_get_fish_uaa(self):
        sp = Species.get("Gaga")
        assert sp.find_matching_gene_name("UAA") is None

    def test_chicken_does_not_get_mammal_drb(self):
        sp = Species.get("Gaga")
        assert sp.find_matching_gene_name("DRB") is None

    def test_frog_does_not_get_mammal_drb(self):
        sp = Species.get("Xela")
        assert sp.find_matching_gene_name("DRB") is None

    def test_parse_hla_uaa_fails(self):
        """HLA-UAA should not parse — UAA is a fish gene, not human."""
        assert parse("HLA-UAA", raise_on_error=False) is None

    def test_parse_satr_dqa_fails(self):
        """Satr-DQA should not parse — DQA is a mammalian gene, not fish."""
        assert parse("Satr-DQA", raise_on_error=False) is None


# ---------------------------------------------------------------------------
# default_species priority
# ---------------------------------------------------------------------------


class TestGalliformInheritance:
    """Galliform species inherit BF, BLB, DMA, DMB1/2, TAP1/2 from parent."""

    def test_galliform_parent_has_genes(self):
        sp = Species.get("Galliformes sp.")
        assert sp is not None
        assert sp.find_matching_gene_name("BF") is not None
        assert sp.find_matching_gene_name("BLB") is not None
        assert sp.find_matching_gene_name("DMA") is not None
        assert sp.find_matching_gene_name("TAP1") is not None

    def test_turkey_inherits_bf(self):
        """Turkey inherits BF from Galliformes sp. parent."""
        result = parse("Mega-BF", raise_on_error=True)
        eq_(result.species.name, "Meleagris gallopavo")

    def test_peafowl_inherits_blb(self):
        result = parse("Pacr-BLB", raise_on_error=True)
        eq_(result.species.name, "Pavo cristatus")

    def test_chicken_still_has_specific_genes(self):
        """Chicken should still have BF1, BF2, YF1, YF2 on top of inherited BF."""
        sp = Species.get("Gaga")
        assert sp.find_matching_gene_name("BF1") is not None
        assert sp.find_matching_gene_name("BF2") is not None
        assert sp.find_matching_gene_name("YF1") is not None

    def test_quail_has_inherited_plus_own(self):
        """Quail inherits BF/BLB from Galliformes and has own class I/II loci."""
        sp = Species.get("Coja")
        assert sp.find_matching_gene_name("BF") is not None  # inherited
        assert sp.find_matching_gene_name("DAB1") is not None  # own

    def test_galliform_does_not_get_fish_genes(self):
        """Galliforms should NOT have fish U-lineage genes."""
        sp = Species.get("Gaga")
        assert sp.find_matching_gene_name("UAA") is None
        assert sp.find_matching_gene_name("UBA") is None

    def test_galliform_does_not_get_mammal_genes(self):
        sp = Species.get("Mega")
        assert sp.find_matching_gene_name("DRB") is None
        assert sp.find_matching_gene_name("DRB1") is None
        assert sp.find_matching_gene_name("DQA1") is None


class TestCrocodyliaInheritance:
    """Crocodilian species inherit UA and DB01-DB08 from Crocodylia sp. parent."""

    def test_crocodylia_parent_has_genes(self):
        sp = Species.get("Crocodylia sp.")
        assert sp is not None
        assert sp.find_matching_gene_name("UA") is not None
        assert sp.find_matching_gene_name("DB01") is not None
        assert sp.find_matching_gene_name("DB08") is not None

    def test_alligator_inherits_db_genes(self):
        """American alligator inherits DB01-DB08 from Crocodylia sp."""
        result = parse("Almi-DB01", raise_on_error=True)
        eq_(result.species.name, "Alligator mississippiensis")

    def test_gharial_inherits_ua(self):
        result = parse("GaviaGange-UA", raise_on_error=True)
        eq_(result.species.name, "Gavialis gangeticus")

    def test_crpo_has_inherited_plus_own(self):
        """Crpo inherits UA/DB01-08 and has own UB, UC, DAA, DAB1, DAB2."""
        sp = Species.get("Crpo")
        assert sp.find_matching_gene_name("UA") is not None  # inherited
        assert sp.find_matching_gene_name("DB01") is not None  # inherited
        assert sp.find_matching_gene_name("UB") is not None  # own
        assert sp.find_matching_gene_name("DAA") is not None  # own

    def test_croc_does_not_get_mammal_genes(self):
        sp = Species.get("Crpo")
        assert sp.find_matching_gene_name("DRB") is None
        assert sp.find_matching_gene_name("DRB1") is None

    def test_croc_does_not_get_galliform_genes(self):
        sp = Species.get("Crpo")
        assert sp.find_matching_gene_name("BF") is None
        assert sp.find_matching_gene_name("BF1") is None
        assert sp.find_matching_gene_name("BLB") is None


class TestDMBInheritance:
    """DMB comes from Gnathostomata root; DMB1/DMB2 from Galliformes or species."""

    def test_chicken_has_dmb_from_root_and_dmb1_from_galliformes(self):
        """Chicken inherits DMB from Gnathostomata AND DMB1/DMB2 from Galliformes."""
        sp = Species.get("Gaga")
        assert sp.find_matching_gene_name("DMB") is not None
        assert sp.find_matching_gene_name("DMB1") is not None
        assert sp.find_matching_gene_name("DMB2") is not None

    def test_turtle_gets_dmb_from_root(self):
        """Turtle inherits DMB from Gnathostomata via Testudines."""
        sp = Species.get("Chelonia mydas")
        assert sp.find_matching_gene_name("DMB") is not None
        assert sp.find_matching_gene_name("DMA") is not None
        assert sp.find_matching_gene_name("TAP1") is not None


class TestDefaultSpeciesPriority:
    """When default_species is provided, it takes priority over gene-inferred species."""

    def test_dma_with_turtle_default(self):
        """Turtle inherits DMA from Gnathostomata root."""
        result = parse("DMA", default_species="Chelonia mydas", raise_on_error=True)
        eq_(result.species.name, "Chelonia mydas")

    def test_tap1_with_tuatara_default(self):
        """Tuatara inherits TAP1 from Gnathostomata root."""
        result = parse("TAP1", default_species="Sphenodon punctatus", raise_on_error=True)
        eq_(result.species.name, "Sphenodon punctatus")

    def test_dmb_with_ostrich_default(self):
        """Ostrich inherits DMB from Gnathostomata root."""
        result = parse("DMB", default_species="Struthio camelus", raise_on_error=True)
        eq_(result.species.name, "Struthio camelus")
