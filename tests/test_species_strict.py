from mhcgnomes import Gene, Species, parse

from .common import eq_


def test_species_lineage_helpers():
    bos = Species.get("Bos sp.")
    bota = Species.get("Bos taurus")
    galliformes = Species.get("Galliformes sp.")
    gaga = Species.get("Gallus gallus")

    assert bos is not None
    assert bota is not None
    assert galliformes is not None
    assert gaga is not None

    assert bos.is_parent_of(bota)
    assert bota.is_child_of(bos)
    assert bos.is_ancestor_of(bota)
    assert bota.is_descendant_of(bos)
    assert galliformes.is_ancestor_of(gaga)
    assert gaga.is_descendant_of(galliformes)


def test_species_strict_exact_match():
    result = parse("HLA-A*02:01", species="Homo sapiens")
    eq_(result.species.name, "Homo sapiens")


def test_species_strict_bola_converts_to_bos_taurus():
    result = parse("BoLA-DRB3*01:01", species="Bos taurus")
    eq_(result.species.name, "Bos taurus")
    eq_(result.to_string(), "Bota-DRB3*01:01")


def test_species_strict_sla_converts_to_sus_scrofa():
    result = parse("SLA-1*01:01", species="Sus scrofa")
    eq_(result.species.name, "Sus scrofa")
    eq_(result.to_string(), "Susc-1*01:01")


def test_species_strict_dla_converts_to_canis_lupus():
    result = parse("DLA-DRB1", species="Canis lupus")
    eq_(result.species.name, "Canis lupus")
    eq_(result.to_string(), "Calu-DRB1")


def test_species_strict_bola_with_bos_sp():
    result = parse("BoLA-DRB3*01:01", species="Bos sp.")
    eq_(result.species.name, "Bos sp.")
    eq_(result.to_string(), "BoLA-DRB3*01:01")


def test_species_strict_hla_with_bos_taurus_errors():
    assert parse("HLA-A*02:01", species="Bos taurus", raise_on_error=False) is None


def test_species_strict_bola_with_human_errors():
    assert parse("BoLA-DRB3*01:01", species="Homo sapiens", raise_on_error=False) is None


def test_species_strict_bola_with_sheep_errors():
    assert parse("BoLA-DRB3*01:01", species="Ovis sp.", raise_on_error=False) is None


def test_species_strict_taxonomic_node_does_not_convert_to_descendant():
    assert parse("Galliformes", species="Gallus gallus", raise_on_error=False) is None


def test_species_strict_child_result_not_cast_up_to_parent():
    assert parse("Gaga-BF1", species="Galliformes sp.", raise_on_error=False) is None


def test_species_strict_context_only_hymo_rescues_silver_carp():
    result = parse("Hymo-DAB", species="Hypophthalmichthys molitrix", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Hypophthalmichthys molitrix")
    eq_(result.to_string(), "HypoMoli-DAB")


def test_species_strict_context_only_orla_rescues_medaka():
    result = parse("ORLA-UAA", species="Oryzias latipes", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Oryzias latipes")
    eq_(result.to_string(), "OryzLati-UAA")


def test_species_strict_context_only_orla_rescues_killifish():
    result = parse("Orla-UAA", species="Iconisemion striatum", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Iconisemion striatum")
    eq_(result.to_string(), "IconStri-UAA")


def test_species_strict_context_only_moal_rescues_swamp_eel():
    result = parse("Moal-DAB", species="Monopterus albus", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Monopterus albus")
    eq_(result.to_string(), "MonoAlbu-DAB")


def test_species_strict_context_only_moal_rescues_white_wagtail():
    result = parse("Moal-DAB4", species="Motacilla alba", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.name, "Motacilla alba")
    eq_(result.to_string(), "MotaAlba-DAB4")
