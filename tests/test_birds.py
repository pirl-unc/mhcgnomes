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


def test_parse_common_tern_species_Sthi():
    expected = Species.get("Sthi")
    assert expected is not None
    eq_(parse("Sthi", raise_on_error=True), expected)


def test_parse_common_tern_family_level_genes_and_alleles():
    examples = [("UA", ("01", "01"), "I"), ("DAB", ("01", "01"), "IIa")]
    for gene_name, fields, mhc_class in examples:
        expected_gene = Gene.get("Sthi", gene_name)
        expected_allele = Allele.get("Sthi", gene_name, fields)
        assert expected_gene is not None
        assert expected_allele is not None
        eq_(expected_gene.mhc_class, mhc_class)
        eq_(parse(f"Sthi-{gene_name}", raise_on_error=True), expected_gene)
        eq_(parse(f"Sthi-{gene_name}*{':'.join(fields)}", raise_on_error=True), expected_allele)


def test_parse_penguin_species_and_DRB1_family():
    for prefix in ["Sphu", "Spma"]:
        species = Species.get(prefix)
        gene = Gene.get(prefix, "DRB1")
        assert species is not None
        assert gene is not None
        eq_(gene.mhc_class, "IIa")
        eq_(parse(prefix, raise_on_error=True), species)
        eq_(parse(f"{prefix}-DRB1", raise_on_error=True), gene)


def test_parse_barn_owl_family_level_and_embedded_prefix_aliases():
    examples = [
        ("Tyal-UA", Gene.get("Tyal", "UA")),
        ("Tyal-MHCIIB", Gene.get("Tyal", "DAB")),
        ("Tyal-DRB", Gene.get("Tyal", "DAB")),
        ("Tyal-MhcTyal-UA", Gene.get("Tyal", "UA")),
        ("Tyal-MhcTyal-DAB", Gene.get("Tyal", "DAB")),
        ("Tyal-MhcTyal-DAB1", Gene.get("Tyal", "DAB1")),
        ("Tyal-MhcTyal-DAB2", Gene.get("Tyal", "DAB2")),
    ]
    for raw_string, expected in examples:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_barn_owl_mhctyal_prefix_alleles():
    examples = [
        ("MhcTyal-UA*01:01", Allele.get("Tyal", "UA", "01", "01")),
        ("MhcTyal-DAB1*01:01", Allele.get("Tyal", "DAB1", "01", "01")),
    ]
    for raw_string, expected in examples:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_chicken_family_level_aliases_without_breaking_specific_loci():
    expected_pairs = [
        ("Gaga-BF", Gene.get("Gaga", "BF")),
        ("Gaga-B-F", Gene.get("Gaga", "BF")),
        ("Gaga-B-LB", Gene.get("Gaga", "BLB")),
        ("Gaga-BLB", Gene.get("Gaga", "BLB")),
        ("Gaga-B-DMA", Gene.get("Gaga", "DMA")),
        ("Gaga-B-DMB2", Gene.get("Gaga", "DMB2")),
        ("Gaga-B-LB12c", Gene.get("Gaga", "B12c")),
        ("Gaga-BF1", Gene.get("Gaga", "BF1")),
        ("Gaga-BF2", Gene.get("Gaga", "BF2")),
        ("Gaga-BF12", Allele.get("Gaga", "BF", "12")),
    ]
    for raw_string, expected in expected_pairs:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_chinese_egret_species_Egeu():
    expected = Species.get("Egeu")
    assert expected is not None
    eq_(parse("Egeu", raise_on_error=True), expected)


def test_parse_chinese_egret_class1_genes():
    for gene_name in ["UAA", "UBA"]:
        expected = Gene.get("Egeu", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, "I")
        eq_(parse(f"Egeu-{gene_name}", raise_on_error=True), expected)


def test_parse_chinese_egret_class2_genes():
    for gene_name in ["DAB1", "DAB2", "DAB3", "DAB4", "DAB5", "DAB6"]:
        expected = Gene.get("Egeu", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, "IIa")
        eq_(parse(f"Egeu-{gene_name}", raise_on_error=True), expected)


def test_parse_chinese_egret_alleles():
    for gene_name in ["UAA", "DAB1", "DAB3"]:
        expected = Allele.get("Egeu", gene_name, "01", "01")
        assert expected is not None
        eq_(parse(f"Egeu-{gene_name}*01:01", raise_on_error=True), expected)


def test_parse_ratite_species():
    for prefix, latin in [
        ("Stca", "Struthio camelus"),
        ("Drno", "Dromaius novaehollandiae"),
        ("Rhpe", "Rhea pennata"),
        ("Rham", "Rhea americana"),
        ("Apau", "Apteryx australis"),
        ("Apow", "Apteryx owenii"),
        ("Casu", "Casuarius casuarius"),
        ("Tima", "Tinamus major"),
    ]:
        expected = Species.get(prefix)
        assert expected is not None, f"Species.get({prefix!r}) returned None"
        eq_(parse(prefix, raise_on_error=True), expected)
        eq_(Species.get(latin), expected)


def test_do_not_parse_ambiguous_or_unreviewed_bird_strings():
    for s in [
        "Gaga-YFV",
        "Gaga-BFw-01",
        "Gaga-BFz-01",
        "Gaga-B-LBII",
        "Coja-II-13*01",
        "Coja-II-16*01",
        "Coja-II-17*01",
        "Ritr-DRB1",
        "Otel-DAB",
        "Phtr-UA",
        "Phco-UA",
    ]:
        assert parse(s, raise_on_error=False) is None
