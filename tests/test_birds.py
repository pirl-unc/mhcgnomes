from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_


def test_parse_great_reed_warbler_species_Acar():
    expected = Species.get("Acar")
    assert expected is not None
    eq_(parse("Acar", raise_on_error=True), expected)


def test_parse_great_reed_warbler_UA_gene_and_allele():
    expected_gene = Gene.get("Acar", "UA")
    expected_allele = Allele.get("Acar", "UA", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Acar-UA", raise_on_error=True), expected_gene)
    eq_(parse("Acar-UA*01:01", raise_on_error=True), expected_allele)


def test_parse_sedge_warbler_species_Acsc():
    expected = Species.get("Acsc")
    assert expected is not None
    eq_(parse("Acsc", raise_on_error=True), expected)


def test_parse_sedge_warbler_UA_gene_and_allele():
    expected_gene = Gene.get("Acsc", "UA")
    expected_allele = Allele.get("Acsc", "UA", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Acsc-UA", raise_on_error=True), expected_gene)
    eq_(parse("Acsc-UA*01:01", raise_on_error=True), expected_allele)


def test_parse_common_yellowthroat_species_Getr():
    expected = Species.get("Getr")
    assert expected is not None
    eq_(parse("Getr", raise_on_error=True), expected)


def test_parse_common_yellowthroat_DAB_gene_and_allele():
    expected_gene = Gene.get("Getr", "DAB")
    expected_allele = Allele.get("Getr", "DAB", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Getr-DAB", raise_on_error=True), expected_gene)
    eq_(parse("Getr-DAB*01:01", raise_on_error=True), expected_allele)


def test_common_yellowthroat_does_not_expose_generic_MHC_gene_alias():
    species = Species.get("Getr")
    assert species is not None
    assert species.find_matching_gene_name("MHC") is None


def test_parse_golden_pheasant_species_Chpi():
    expected = Species.get("Chpi")
    assert expected is not None
    eq_(parse("Chpi", raise_on_error=True), expected)


def test_parse_golden_pheasant_class1_genes():
    expected_classes = {"IA1": "Ia", "IA2": "Ia", "IA3": "Ib"}
    for gene_name in ["IA1", "IA2", "IA3"]:
        expected = Gene.get("Chpi", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, expected_classes[gene_name])
        eq_(parse(f"Chpi-{gene_name}", raise_on_error=True), expected)


def test_parse_japanese_quail_species_Coja():
    expected = Species.get("Coja")
    assert expected is not None
    eq_(parse("Coja", raise_on_error=True), expected)


def test_parse_japanese_quail_named_class2_beta_loci():
    examples = [
        ("DAB1", "01"),
        ("DBB1", "01"),
        ("DCB1", "02"),
        ("DDB1", "01"),
        ("DEB1", "02"),
        ("DFB1", "01"),
        ("DGB1", "01"),
    ]
    for gene_name, field in examples:
        expected_gene = Gene.get("Coja", gene_name)
        expected_allele = Allele.get("Coja", gene_name, field)
        assert expected_gene is not None
        assert expected_allele is not None
        eq_(expected_gene.mhc_class, "IIa")
        eq_(parse(f"Coja-{gene_name}", raise_on_error=True), expected_gene)
        eq_(parse(f"Coja-{gene_name}*{field}", raise_on_error=True), expected_allele)


def test_parse_eurasian_coot_species_Fuat():
    expected = Species.get("Fuat")
    assert expected is not None
    eq_(parse("Fuat", raise_on_error=True), expected)


def test_parse_eurasian_coot_DAB_gene_and_example_allele():
    expected_gene = Gene.get("Fuat", "DAB")
    expected_allele = Allele.get("Fuat", "DAB", "199")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(expected_gene.mhc_class, "IIa")
    eq_(parse("Fuat-DAB", raise_on_error=True), expected_gene)
    eq_(parse("Fuat-DAB*199", raise_on_error=True), expected_allele)


def test_parse_penguin_species_and_DRB1_family():
    for prefix in ["Sphu", "Spma"]:
        species = Species.get(prefix)
        gene = Gene.get(prefix, "DRB1")
        assert species is not None
        assert gene is not None
        eq_(gene.mhc_class, "IIa")
        eq_(parse(prefix, raise_on_error=True), species)
        eq_(parse(f"{prefix}-DRB1", raise_on_error=True), gene)


def test_do_not_parse_ambiguous_bird_strings():
    for s in [
        "Gaga-BF",
        "Gaga-B-LB",
        "Gaga-YFV",
        "Coja-II-13*01",
        "Coja-II-16*01",
        "Coja-II-17*01",
        "Ritr-DRB1",
        "Tyal-UA",
        "Otel-DAB",
    ]:
        assert parse(s, raise_on_error=False) is None
