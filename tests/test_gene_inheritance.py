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


class TestCommonGenes:
    """DMA, TAP1, TAP2, TAPBP, B2M accepted for any species."""

    @pytest.mark.parametrize(
        "latin",
        [
            "Chelonia mydas",
            "Struthio camelus",
            "Crocodylus porosus",
            "Sphenodon punctatus",
        ],
    )
    def test_common_genes_work_for_species_without_explicit_genes(self, latin):
        sp = Species.get(latin)
        assert sp is not None
        for gene in ["DMA", "TAP1"]:
            assert sp.find_matching_gene_name(gene) is not None, (
                f"{latin} should accept common gene {gene}"
            )

    def test_common_gene_with_default_species(self):
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


class TestDefaultSpeciesPriority:
    """When default_species is provided, it takes priority over gene-inferred species."""

    def test_mhciib_with_ostrich_default(self):
        result = parse("MHCIIB", default_species="Struthio camelus", raise_on_error=False)
        assert result is not None
        eq_(result.species.name, "Struthio camelus")

    def test_dma_with_turtle_default(self):
        result = parse("DMA", default_species="Chelonia mydas", raise_on_error=True)
        eq_(result.species.name, "Chelonia mydas")

    def test_tap1_with_tuatara_default(self):
        result = parse("TAP1", default_species="Sphenodon punctatus", raise_on_error=True)
        eq_(result.species.name, "Sphenodon punctatus")
