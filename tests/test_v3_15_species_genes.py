"""
Tests for v3.15.0 additions: new species, genes, prefixes,
cetacean class II inheritance, and trailing-MHC prefix stripping.
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# Trailing-MHC prefix stripping (general mechanism)
# ---------------------------------------------------------------------------


class TestTrailingMhcStrip:
    """ManaMHC-DAB*01 style: trailing MHC suffix on species prefix."""

    def test_mana_mhc_allele(self):
        result = parse("ManaMHC-DAB*01", raise_on_error=True)
        eq_(result.species.name, "Manacus sp.")
        eq_(result.gene.name, "DAB")

    def test_mana_mhc_gene(self):
        result = parse("ManaMHC-UA", raise_on_error=True)
        eq_(result.species.name, "Manacus sp.")
        eq_(result.name, "UA")

    def test_mana_mhc_case_insensitive(self):
        result = parse("ManaMhc-DAB*01", raise_on_error=True)
        eq_(result.species.name, "Manacus sp.")

    def test_trailing_mhc_does_not_break_normal_parsing(self):
        """HLA-A*02:01 should NOT be affected by trailing MHC strip."""
        result = parse("HLA-A*02:01", raise_on_error=True)
        eq_(result.species.name, "Homo sapiens")

    def test_trailing_mhc_does_not_break_leading_mhc(self):
        """MhcTyal-DAB1*01:01 still works (leading Mhc strip)."""
        result = parse("MhcTyal-DAB1*01:01", raise_on_error=True)
        eq_(result.species.prefix, "TytoAlba")

    def test_bare_mana_still_works(self):
        """Mana-DAB*01 (without MHC suffix) should still parse."""
        result = parse("Mana-DAB*01", raise_on_error=True)
        eq_(result.species.name, "Manacus sp.")


# ---------------------------------------------------------------------------
# New species
# ---------------------------------------------------------------------------


class TestNewSpeciesV315:
    """Species added in v3.15.0."""

    @pytest.mark.parametrize(
        "prefix, latin",
        [
            ("Cape", "Caperea marginata"),
            ("Rhsi", "Rhinopithecus strykeri"),
            ("Mygl", "Myodes glareolus"),
            ("Clgl", "Myodes glareolus"),  # synonym prefix
            ("Odhe", "Odocoileus hemionus"),
            ("Loaf", "Loxodonta africana"),
            ("Nesc", "Neomonachus schauinslandi"),
            ("Dele", "Delphinapterus leucas"),
            ("Oror", "Orcinus orca"),
            ("Phca", "Physeter macrocephalus"),
            ("Igig", "Iguana iguana"),
        ],
    )
    def test_new_species_lookup(self, prefix, latin):
        sp = Species.get(prefix)
        assert sp is not None, f"Species.get({prefix!r}) returned None"
        eq_(sp.name, latin)

    def test_manacus_species(self):
        sp = Species.get("Mana")
        assert sp is not None
        eq_(sp.name, "Manacus sp.")

    def test_myodes_synonym(self):
        """Clethrionomys glareolus is a synonym for Myodes glareolus."""
        sp = Species.get("Clethrionomys glareolus")
        assert sp is not None
        eq_(sp.name, "Myodes glareolus")


# ---------------------------------------------------------------------------
# Missing prefixes for existing species
# ---------------------------------------------------------------------------


class TestMissingPrefixes:
    """Alternative 3-letter prefixes for primates and other species."""

    def test_ppa_bonobo(self):
        sp = Species.get("Ppa")
        assert sp is not None
        eq_(sp.name, "Pan paniscus")

    def test_ptr_chimpanzee(self):
        sp = Species.get("Ptr")
        assert sp is not None
        eq_(sp.name, "Pan troglodytes")

    def test_gbb_gorilla(self):
        sp = Species.get("Gbb")
        assert sp is not None
        eq_(sp.name, "Gorilla beringei")

    def test_gbg_gorilla(self):
        sp = Species.get("Gbg")
        assert sp is not None
        eq_(sp.name, "Gorilla beringei")

    def test_ggg_gorilla(self):
        sp = Species.get("Ggg")
        assert sp is not None
        eq_(sp.name, "Gorilla gorilla")

    def test_caur_goldfish(self):
        sp = Species.get("Caur")
        assert sp is not None
        eq_(sp.name, "Carassius auratus")


# ---------------------------------------------------------------------------
# Cetacean class II inheritance
# ---------------------------------------------------------------------------


class TestCetaceaClassII:
    """All cetaceans inherit mammalian class II from Cetacea sp."""

    @pytest.mark.parametrize(
        "gene",
        ["DQA1", "DQB1", "DRA", "DRB", "DRB1", "DPA1", "DPB1", "DOA", "DOB", "DMA", "DMB"],
    )
    def test_cetacea_clade_has_gene(self, gene):
        sp = Species.get("Cetacea sp.")
        assert sp.find_matching_gene_name(gene) is not None, gene

    def test_dolphin_inherits_dqa1(self):
        sp = Species.get("Tutr")
        assert sp.find_matching_gene_name("DQA1") is not None

    def test_dolphin_inherits_dqb1(self):
        sp = Species.get("Tutr")
        assert sp.find_matching_gene_name("DQB1") is not None

    def test_dolphin_inherits_doa(self):
        sp = Species.get("Tutr")
        assert sp.find_matching_gene_name("DOA") is not None

    def test_orca_inherits_class_ii(self):
        sp = Species.get("Orcinus orca")
        assert sp.find_matching_gene_name("DQA1") is not None
        assert sp.find_matching_gene_name("DPB1") is not None

    def test_beluga_inherits_class_ii(self):
        sp = Species.get("Delphinapterus leucas")
        assert sp.find_matching_gene_name("DRB1") is not None

    def test_parse_tutr_dqb1_allele(self):
        result = parse("Tutr-DQB1*01:01", raise_on_error=True)
        eq_(result.species.name, "Tursiops truncatus")


# ---------------------------------------------------------------------------
# Missing genes on existing species
# ---------------------------------------------------------------------------


class TestMissingGenesV315:
    """Genes added to existing species."""

    def test_salmon_uga(self):
        sp = Species.get("Sasa")
        assert sp.find_matching_gene_name("UGA") is not None

    def test_salmon_uha(self):
        sp = Species.get("Sasa")
        assert sp.find_matching_gene_name("UHA") is not None

    def test_salmon_ze(self):
        sp = Species.get("Sasa")
        assert sp.find_matching_gene_name("ZE") is not None

    def test_iguana_ub(self):
        sp = Species.get("AmblCris")
        assert sp.find_matching_gene_name("UB") is not None

    def test_koala_uh(self):
        sp = Species.get("PhasCine")
        assert sp.find_matching_gene_name("UH") is not None

    def test_equus_dqa_family(self):
        sp = Species.get("ELA")
        assert sp.find_matching_gene_name("DQA") is not None

    def test_equus_dqb_family(self):
        sp = Species.get("ELA")
        assert sp.find_matching_gene_name("DQB") is not None

    def test_equus_drb_family(self):
        sp = Species.get("ELA")
        assert sp.find_matching_gene_name("DRB") is not None
