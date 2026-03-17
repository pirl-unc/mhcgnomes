"""
Tests for taxonomic gene inheritance and cross-taxon leak prevention.

Species inherit genes from their parent node (e.g., salmonids from
Salmonidae sp.). Root-level transport and DM genes come from
Gnathostomata sp. through the tree.
Taxon-specific genes must NOT leak across boundaries.
"""

import pytest

from mhcgnomes import Gene, MhcClass, Species, parse
from mhcgnomes.species import raw_species_dict

from .common import eq_

GNATHOSTOMATA = "Gnathostomata sp."
ROOTED_SPECIES = sorted(latin for latin in raw_species_dict if latin != GNATHOSTOMATA)
INTENTIONALLY_UNROOTED = set()


def has_ancestor(species, ancestor_name):
    current = species
    while current is not None:
        if current.name == ancestor_name:
            return True
        current = current.parent_species
    return False


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


class TestRootTransportGenesAndAliases:
    """All rooted species inherit the jawed-vertebrate transport/DM core."""

    @pytest.mark.parametrize("latin", ROOTED_SPECIES)
    def test_all_species_descend_from_gnathostomata(self, latin):
        sp = Species.get(latin)
        assert sp is not None
        assert has_ancestor(sp, GNATHOSTOMATA), latin

    def test_only_intentionally_unrooted_species_lack_root_ancestor(self):
        unrooted = {
            latin
            for latin in raw_species_dict
            if latin != GNATHOSTOMATA and not has_ancestor(Species.get(latin), GNATHOSTOMATA)
        }
        eq_(unrooted, INTENTIONALLY_UNROOTED)

    @pytest.mark.parametrize("latin", ROOTED_SPECIES)
    def test_all_species_inherit_root_transport_and_dm_genes(self, latin):
        sp = Species.get(latin)
        assert sp is not None
        for gene_name in ["DMA", "DMB", "TAP1", "TAP2", "TAP-L", "TAPBP", "B2M"]:
            assert sp.find_matching_gene_name(gene_name) is not None, (latin, gene_name)
        assert sp.find_matching_class2_locus_name("DM") is not None, latin

    @pytest.mark.parametrize(
        "alias, expected",
        [
            ("ABCB2", "TAP1"),
            ("RING4", "TAP1"),
            ("PSF1", "TAP1"),
            ("HAM1", "TAP1"),
            ("ABCB3", "TAP2"),
            ("RING11", "TAP2"),
            ("PSF2", "TAP2"),
            ("HAM2", "TAP2"),
            ("ABCB9", "TAP-L"),
            ("TAPL", "TAP-L"),
        ],
    )
    def test_transport_aliases_parse_to_canonical_root_genes(self, alias, expected):
        result = parse(alias, default_species="Struthio camelus", raise_on_error=True)
        eq_(result.species.name, "Struthio camelus")
        eq_(result.name, expected)

    @pytest.mark.parametrize("raw", ["TAP1", "TAP2", "TAP-L", "TAPBP", "B2M"])
    def test_root_other_genes_parse_with_default_species(self, raw):
        result = parse(raw, default_species="Struthio camelus", raise_on_error=True)
        eq_(result.species.name, "Struthio camelus")
        eq_(result.name, raw)

    def test_dm_locus_parses_with_default_species(self):
        result = parse("DM", default_species="Struthio camelus", raise_on_error=True)
        eq_(result.species.name, "Struthio camelus")
        eq_(result.name, "DM")


class TestMhciibScoping:
    """MHCIIB is only accepted for species that actually use that alias."""

    def test_mhciib_parses_as_mhc_class_for_any_species(self):
        """MHCIIB is now a generic class II beta label, works for any species."""
        result = parse("MHCIIB", default_species="Struthio camelus", raise_on_error=True)
        assert isinstance(result, MhcClass)
        eq_(result.chain, "beta")
        eq_(result.species.name, "Struthio camelus")

    def test_mhciib_with_strict_species(self):
        result = parse("MHCIIB", species="Struthio camelus", raise_on_error=True)
        assert isinstance(result, MhcClass)
        eq_(result.species.name, "Struthio camelus")

    def test_mhciib_parses_as_mhc_class_not_gene(self):
        """MHCIIB is now a class II beta MhcClass, not a Gene(Tyal, DAB)."""
        result = parse("MHCIIB", default_species="Tyto alba", raise_on_error=True)
        assert isinstance(result, MhcClass)
        eq_(result.mhc_class, "II")
        eq_(result.chain, "beta")


class TestSpeciesStrictness:
    """species= should reject mismatched species, including Species results."""

    def test_species_argument_rejects_mismatched_species_result(self):
        assert parse("HLA", species="H-2", raise_on_error=False) is None

    def test_species_argument_rejects_mismatched_taxonomic_node(self):
        assert parse("Galliformes", species="Gallus gallus", raise_on_error=False) is None

    def test_species_argument_accepts_matching_taxonomic_node(self):
        result = parse("Galliformes", species="Galliformes sp.", raise_on_error=True)
        eq_(result.name, "Galliformes sp.")


class TestTaxonomicPrefixLeakage:
    """Taxonomic node prefixes must not resolve child-only genes or outputs."""

    @pytest.mark.parametrize("raw", ["Galliformes-BF1", "Crocodylia-UB", "Salmonidae-UEA"])
    def test_taxonomic_prefixes_do_not_resolve_child_specific_genes(self, raw):
        assert parse(raw, raise_on_error=False) is None

    @pytest.mark.parametrize(
        "species_prefix, gene_name, expected_string",
        [
            ("Crpo", "UB", "Crpo-UB"),
            ("Gaga", "BF1", "Gaga-BF1"),
            ("Satr", "UBA", "Satr-UBA"),
        ],
    )
    def test_use_old_species_prefix_does_not_emit_taxonomic_prefix(
        self, species_prefix, gene_name, expected_string
    ):
        gene = Gene.get(species_prefix, gene_name)
        assert gene is not None
        eq_(gene.to_string(use_old_species_prefix=True), expected_string)
