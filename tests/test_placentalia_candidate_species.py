import pytest

from mhcgnomes import Species, parse

from .common import eq_


class TestPlacentaliaCore:
    @pytest.mark.parametrize(
        "gene",
        [
            "DQA",
            "DQA1",
            "DQB",
            "DQB1",
            "DRA",
            "DRB",
            "DRB1",
            "DPA1",
            "DPB1",
            "DOA",
            "DOB",
            "DMA",
            "DMB",
            "TAP1",
            "TAP2",
            "TAPBP",
            "B2M",
        ],
    )
    def test_placentalia_has_shared_mammalian_core(self, gene):
        sp = Species.get("Placentalia sp.")
        assert sp is not None
        assert sp.find_matching_gene_name(gene) is not None, gene

    def test_existing_bank_vole_now_inherits_dqb_shorthand(self):
        result = parse("Mygl-DQB*01", raise_on_error=True)
        eq_(result.species.name, "Myodes glareolus")
        eq_(result.gene.name, "DQB")

    def test_existing_dog_now_inherits_do_family(self):
        result = parse("DLA-DOB", raise_on_error=True)
        eq_(result.species.name, "Canis sp.")
        eq_(result.name, "DOB")


class TestNewCandidateSpecies:
    @pytest.mark.parametrize(
        "prefix,latin,raw",
        [
            ("Anda", "Andrias davidianus", "Anda-DAB1*01"),
            ("Phph", "Phocoena phocoena", "Phph-DQB*01"),
            ("Odvi", "Odocoileus virginianus", "Odvi-DRB*01"),
            ("Noal", "Noctilio albiventris", "Noal-DRB*01"),
            ("Phho", "Phocarctos hookeri", "Phho-DRB*01"),
            ("Rhpu", "Rhabdomys pumilio", "Rhpu-DQB*01"),
        ],
    )
    def test_species_lookup_and_parse(self, prefix, latin, raw):
        sp = Species.get(prefix)
        assert sp is not None, prefix
        eq_(sp.name, latin)
        eq_(Species.get(latin), sp)

        result = parse(raw, raise_on_error=True)
        eq_(result.species.name, latin)
