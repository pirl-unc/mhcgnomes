from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_


def test_parse_existing_snake_species_sica():
    expected = Species.get("Sica")
    assert expected is not None
    eq_(parse("Sica"), expected)


def test_parse_existing_snake_gene_sica_daa():
    expected = Gene.get("Sica", "DAA")
    assert expected is not None
    eq_(parse("Sica-DAA"), expected)


def test_parse_existing_snake_allele_sica_daa_01_01():
    expected = Allele.get("Sica", "DAA", "01", "01")
    assert expected is not None
    eq_(parse("Sica-DAA*01:01"), expected)


def test_parse_existing_frog_species_xela():
    expected = Species.get("Xela")
    assert expected is not None
    eq_(parse("Xela"), expected)


def test_parse_existing_frog_gene_xela_uaa():
    expected = Gene.get("Xela", "UAA")
    assert expected is not None
    eq_(parse("Xela-UAA"), expected)


def test_parse_existing_frog_allele_xela_uaa_01_01():
    expected = Allele.get("Xela", "UAA", "01", "01")
    assert expected is not None
    eq_(parse("Xela-UAA*01:01"), expected)


def test_parse_frog_gene_xela_uba():
    expected = Gene.get("Xela", "UBA")
    assert expected is not None
    eq_(parse("Xela-UBA"), expected)


def test_parse_frog_gene_xela_uca():
    expected = Gene.get("Xela", "UCA")
    assert expected is not None
    eq_(parse("Xela-UCA"), expected)


def test_parse_frog_gene_xela_daa():
    expected = Gene.get("Xela", "DAA")
    assert expected is not None
    eq_(parse("Xela-DAA"), expected)


def test_parse_frog_gene_xela_dab():
    expected = Gene.get("Xela", "DAB")
    assert expected is not None
    eq_(parse("Xela-DAB"), expected)


def test_parse_frog_gene_xela_dma():
    expected = Gene.get("Xela", "DMA")
    assert expected is not None
    eq_(parse("Xela-DMA"), expected)


def test_parse_frog_allele_xela_uba_01_01():
    expected = Allele.get("Xela", "UBA", "01", "01")
    assert expected is not None
    eq_(parse("Xela-UBA*01:01"), expected)


def test_parse_frog_allele_xela_dab_01_01():
    expected = Allele.get("Xela", "DAB", "01", "01")
    assert expected is not None
    eq_(parse("Xela-DAB*01:01"), expected)


def test_parse_pilot_frog_species_xetr():
    expected = Species.get("Xetr")
    assert expected is not None
    eq_(parse("Xetr"), expected)
    eq_(Species.get("Xenopus tropicalis"), expected)


def test_parse_frog_gene_xetr_uaa():
    expected = Gene.get("Xetr", "UAA")
    assert expected is not None
    eq_(parse("Xetr-UAA"), expected)


def test_parse_frog_gene_xetr_uba():
    expected = Gene.get("Xetr", "UBA")
    assert expected is not None
    eq_(parse("Xetr-UBA"), expected)


def test_parse_frog_gene_xetr_uca():
    expected = Gene.get("Xetr", "UCA")
    assert expected is not None
    eq_(parse("Xetr-UCA"), expected)


def test_parse_frog_gene_xetr_daa():
    expected = Gene.get("Xetr", "DAA")
    assert expected is not None
    eq_(parse("Xetr-DAA"), expected)


def test_parse_frog_gene_xetr_dab():
    expected = Gene.get("Xetr", "DAB")
    assert expected is not None
    eq_(parse("Xetr-DAB"), expected)


def test_parse_frog_gene_xetr_dma():
    expected = Gene.get("Xetr", "DMA")
    assert expected is not None
    eq_(parse("Xetr-DMA"), expected)


def test_parse_frog_gene_xetr_tap1():
    expected = Gene.get("Xetr", "TAP1")
    assert expected is not None
    eq_(parse("Xetr-TAP1"), expected)


def test_parse_frog_allele_xetr_uaa_01_01():
    expected = Allele.get("Xetr", "UAA", "01", "01")
    assert expected is not None
    eq_(parse("Xetr-UAA*01:01"), expected)


def test_parse_frog_allele_xetr_dab_01_01():
    expected = Allele.get("Xetr", "DAB", "01", "01")
    assert expected is not None
    eq_(parse("Xetr-DAB*01:01"), expected)


# ---------------------------------------------------------------------------
# Other frogs
# ---------------------------------------------------------------------------


def test_parse_omei_tree_frog_species_zhom():
    expected = Species.get("Zhom")
    assert expected is not None
    eq_(parse("Zhom", raise_on_error=True), expected)
    eq_(Species.get("Zhangixalus omeimontis"), expected)


def test_parse_omei_tree_frog_dab():
    expected = Gene.get("Zhom", "DAB")
    assert expected is not None
    eq_(expected.mhc_class, "IIa")
    eq_(parse("Zhom-DAB", raise_on_error=True), expected)


def test_parse_omei_tree_frog_rhom_beta1_alias():
    """Old-genus Rhom-beta1 alias should resolve to DAB."""
    expected = Gene.get("Zhom", "DAB")
    assert expected is not None
    eq_(parse("Zhom-Rhom-beta1", raise_on_error=True), expected)


def test_parse_omei_tree_frog_allele():
    expected = Allele.get("Zhom", "DAB", "01")
    assert expected is not None
    eq_(parse("Zhom-DAB*01", raise_on_error=True), expected)


# ---------------------------------------------------------------------------
# Crocodilians
# ---------------------------------------------------------------------------


def test_parse_crocodilian_species():
    for prefix, latin in [
        ("Crpo", "Crocodylus porosus"),
        ("Meca", "Mecistops cataphractus"),
        ("Oste", "Osteolaemus tetraspis"),
        ("Crni", "Crocodylus niloticus"),
        ("Tosc", "Tomistoma schlegelii"),
    ]:
        expected = Species.get(prefix)
        assert expected is not None, f"Species.get({prefix!r}) returned None"
        eq_(parse(prefix, raise_on_error=True), expected)
        eq_(Species.get(latin), expected)


def test_parse_crpo_expanded_genes():
    """Crpo has class I UA/UB/UC and class II DAA/DAB1/DAB2."""
    for gene_name, mhc_class in [
        ("UA", "I"),
        ("UB", "I"),
        ("UC", "I"),
        ("DAA", "IIa"),
        ("DAB1", "IIa"),
        ("DAB2", "IIa"),
    ]:
        expected = Gene.get("Crpo", gene_name)
        assert expected is not None, f"Gene.get('Crpo', '{gene_name}') returned None"
        eq_(expected.mhc_class, mhc_class)
        eq_(parse(f"Crpo-{gene_name}", raise_on_error=True), expected)


# ---------------------------------------------------------------------------
# Turtles
# ---------------------------------------------------------------------------


def test_parse_turtle_species():
    for prefix, latin in [
        ("CaretCaret", "Caretta caretta"),
        ("Chmy", "Chelonia mydas"),
        ("Deco", "Dermochelys coriacea"),
        ("Leke", "Lepidochelys kempii"),
        ("Chse", "Chelydra serpentina"),
        ("ChrysPicta", "Chrysemys picta"),
        ("Pesi", "Pelodiscus sinensis"),
        ("Tetr", "Terrapene triunguis"),
        ("Gopo", "Gopherus polyphemus"),
        ("Chab", "Chelonoidis abingdonii"),
    ]:
        expected = Species.get(prefix)
        assert expected is not None, f"Species.get({prefix!r}) returned None"
        eq_(parse(prefix, raise_on_error=True), expected)
        eq_(Species.get(latin), expected)


# ---------------------------------------------------------------------------
# Lizards
# ---------------------------------------------------------------------------


def test_parse_pilot_lizard_species_anca():
    expected = Species.get("Anca")
    assert expected is not None
    eq_(parse("Anca"), expected)
    eq_(Species.get("Anolis carolinensis"), expected)


def test_parse_pilot_lizard_species_ansa():
    expected = Species.get("Ansa")
    assert expected is not None
    eq_(parse("Ansa"), expected)
    eq_(Species.get("Anolis sagrei"), expected)


# ---------------------------------------------------------------------------
# Crocodilians
# ---------------------------------------------------------------------------


def test_parse_crocodile_species_crpo():
    expected = Species.get("Crpo")
    assert expected is not None
    eq_(parse("Crpo", raise_on_error=True), expected)
    eq_(Species.get("Crocodylus porosus"), expected)


def test_parse_crocodile_gene_ua():
    expected = Gene.get("Crpo", "UA")
    assert expected is not None
    eq_(expected.mhc_class, "I")
    eq_(parse("Crpo-UA", raise_on_error=True), expected)


def test_parse_crocodile_gene_dab1():
    expected = Gene.get("Crpo", "DAB1")
    assert expected is not None
    eq_(expected.mhc_class, "IIa")
    eq_(parse("Crpo-DAB1", raise_on_error=True), expected)


# ---------------------------------------------------------------------------
# Marsupials
# ---------------------------------------------------------------------------


def test_parse_opossum_species_modo():
    expected = Species.get("Modo")
    assert expected is not None
    eq_(parse("Modo", raise_on_error=True), expected)
    eq_(Species.get("Monodelphis domestica"), expected)


def test_parse_opossum_class1_genes():
    for gene_name in ["UA", "UB", "UC", "UG", "UK", "UM", "UT3", "UT5", "UT7", "UT8"]:
        expected = Gene.get("Modo", gene_name)
        assert expected is not None, f"Gene.get('Modo', '{gene_name}') returned None"
        eq_(expected.mhc_class, "I")
        eq_(parse(f"Modo-{gene_name}", raise_on_error=True), expected)


def test_parse_opossum_class2_dab():
    expected = Gene.get("Modo", "DAB")
    assert expected is not None
    eq_(expected.mhc_class, "IIa")
    eq_(parse("Modo-DAB", raise_on_error=True), expected)


def test_parse_opossum_allele():
    expected = Allele.get("Modo", "UT3", "01")
    assert expected is not None
    eq_(parse("Modo-UT3*01", raise_on_error=True), expected)


def test_parse_devil_species_saha():
    expected = Species.get("Saha")
    assert expected is not None
    eq_(parse("Saha", raise_on_error=True), expected)
    eq_(Species.get("Sarcophilus harrisii"), expected)


def test_parse_devil_class1_genes():
    for gene_name in ["UA", "UB", "UC", "UK", "UM"]:
        expected = Gene.get("Saha", gene_name)
        assert expected is not None, f"Gene.get('Saha', '{gene_name}') returned None"
        eq_(expected.mhc_class, "I")
        eq_(parse(f"Saha-{gene_name}", raise_on_error=True), expected)


def test_parse_devil_class2_dab():
    expected = Gene.get("Saha", "DAB")
    assert expected is not None
    eq_(expected.mhc_class, "IIa")
    eq_(parse("Saha-DAB", raise_on_error=True), expected)
