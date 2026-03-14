from mhcgnomes import Allele, Gene, Pair, Species, parse

from .common import eq_


def test_parse_trout_species_Onmy():
    expected = Species.get("Onmy")
    assert expected is not None
    result = parse("Onmy", raise_on_error=True)
    assert result is not None
    eq_(result, expected)


def test_parse_trout_gene_Onmy_DAB():
    result = parse("Onmy-DAB", raise_on_error=True)
    expected = Gene.get("Onmy", "DAB")
    assert expected is not None
    eq_(result, expected)


def test_parse_trout_allele_Onmy_DAB_0501():
    result = parse("Onmy-DAB*0501", raise_on_error=True)
    expected = Allele.get("Onmy", "DAB", ["05", "01"])
    assert expected is not None
    eq_(result, expected)


def test_parse_trout_allele_Onmy_DAB_050101():
    result = parse("Onmy-DAB*050101", raise_on_error=True)
    expected = Allele.get("Onmy", "DAB", ["05", "01", "01"])
    assert expected is not None
    eq_(result, expected)


def test_parse_trout_gene_alias_Onmy_DAA1():
    result = parse("Onmy-DAA1", raise_on_error=True)
    expected = Gene.get("Onmy", "DAA")
    assert expected is not None
    eq_(result, expected)


def test_parse_trout_allele_alias_Onmy_DAA1_01_01():
    result = parse("Onmy-DAA1*01:01", raise_on_error=True)
    expected = Allele.get("Onmy", "DAA", ["01", "01"])
    assert expected is not None
    eq_(result, expected)


def test_parse_salmon_gene_alias_Sasa_DAA1():
    result = parse("Sasa-DAA1", raise_on_error=True)
    expected = Gene.get("Sasa", "DAA")
    assert expected is not None
    eq_(result, expected)


def test_parse_salmon_allele_alias_Sasa_DAA1_01_01():
    result = parse("Sasa-DAA1*01:01", raise_on_error=True)
    expected = Allele.get("Sasa", "DAA", ["01", "01"])
    assert expected is not None
    eq_(result, expected)


def test_parse_grass_carp_B2M_1_ii_star_sep():
    expected = Allele.get("Ctid", "B2M-1", "ii")
    result = parse("Ctid-B2M-1*ii")
    eq_(result, expected)


def test_parse_grass_carp_B2M_1_ii_dash_sep():
    expected = Allele.get("Ctid", "B2M-1", "ii")
    result = parse("Ctid-B2M-1-ii")
    eq_(result, expected)


def test_parse_grass_carp_mhc1_pair_UAA_B2M_1_ii_dash_sep():
    expected = Pair(alpha=Gene.get("Ctid", "UAA"), beta=Allele.get("Ctid", "B2M-1", "ii"))
    result = parse("Ctid-UAA/B2M-1-ii")
    eq_(result, expected)


def test_parse_grass_carp_mhc1_pair_UAA_B2M_1_ii_star_sep():
    expected = Pair(alpha=Gene.get("Ctid", "UAA"), beta=Allele.get("Ctid", "B2M-1", "ii"))
    result = parse("Ctid-UAA/B2M-1*ii")
    eq_(result, expected)


def test_parse_olive_flounder_species_Paol():
    expected = Species.get("Paol")
    assert expected is not None
    eq_(parse("Paol", raise_on_error=True), expected)


def test_parse_zebrafish_species_Dare():
    expected = Species.get("Dare")
    assert expected is not None
    eq_(parse("Dare", raise_on_error=True), expected)


def test_parse_zebrafish_UBA_gene_and_allele():
    expected_gene = Gene.get("Dare", "UBA")
    expected_allele = Allele.get("Dare", "UBA", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(expected_gene.mhc_class, "Ia")
    eq_(parse("Dare-UBA", raise_on_error=True), expected_gene)
    eq_(parse("Dare-UBA*01", raise_on_error=True), expected_allele)


def test_parse_common_carp_species_Cyca():
    expected = Species.get("Cyca")
    assert expected is not None
    eq_(parse("Cyca", raise_on_error=True), expected)


def test_parse_common_carp_family_level_genes():
    expected_classes = {"UA": "I", "ZE": "I", "DXA": "IIa", "DAB": "IIa"}
    for gene_name in ["UA", "ZE", "DXA", "DAB"]:
        expected = Gene.get("Cyca", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, expected_classes[gene_name])
        eq_(parse(f"Cyca-{gene_name}", raise_on_error=True), expected)


def test_parse_common_carp_aliases_to_conservative_family_genes():
    examples = [
        ("Cyca-UA1", Gene.get("Cyca", "UA")),
        ("Cyca-DXA1", Gene.get("Cyca", "DXA")),
        ("Cyca-DXA2", Gene.get("Cyca", "DXA")),
        ("Cyca-DAB1", Gene.get("Cyca", "DAB")),
        ("Cyca-DAB2", Gene.get("Cyca", "DAB")),
        ("Cyca-DAB3", Gene.get("Cyca", "DAB")),
        ("Cyca-DAB4", Gene.get("Cyca", "DAB")),
    ]
    for raw_string, expected in examples:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_common_carp_alias_alleles():
    examples = [
        ("Cyca-UA1*01", Allele.get("Cyca", "UA", "01")),
        ("Cyca-DXA1*01", Allele.get("Cyca", "DXA", "01")),
        ("Cyca-DXA2*01", Allele.get("Cyca", "DXA", "01")),
        ("Cyca-DAB1*01", Allele.get("Cyca", "DAB", "01")),
        ("Cyca-DAB3*01", Allele.get("Cyca", "DAB", "01")),
        ("Cyca-DAB4*01", Allele.get("Cyca", "DAB", "01")),
        ("Cyca-ZE*01:01", Allele.get("Cyca", "ZE", "01", "01")),
    ]
    for raw_string, expected in examples:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_nile_tilapia_species_Orni():
    expected = Species.get("Orni")
    assert expected is not None
    eq_(parse("Orni", raise_on_error=True), expected)


def test_parse_nile_tilapia_genes_and_example_alleles():
    examples = [
        ("DAA", ("05", "01")),
        ("DAB", ("02", "01")),
    ]
    for gene_name, fields in examples:
        expected_gene = Gene.get("Orni", gene_name)
        expected_allele = Allele.get("Orni", gene_name, fields)
        assert expected_gene is not None
        assert expected_allele is not None
        eq_(expected_gene.mhc_class, "IIa")
        eq_(parse(f"Orni-{gene_name}", raise_on_error=True), expected_gene)
        eq_(
            parse(
                f"Orni-{gene_name}*{':'.join(fields)}",
                raise_on_error=True,
            ),
            expected_allele,
        )


def test_parse_olive_flounder_genes():
    for gene_name in ["Ia1", "Ia2", "DAA", "DAB"]:
        expected = Gene.get("Paol", gene_name)
        assert expected is not None
        eq_(parse(f"Paol-{gene_name}", raise_on_error=True), expected)


def test_parse_olive_flounder_alleles():
    for gene_name in ["Ia1", "Ia2", "DAA", "DAB"]:
        expected = Allele.get("Paol", gene_name, "01", "01")
        assert expected is not None
        eq_(parse(f"Paol-{gene_name}*01:01", raise_on_error=True), expected)


def test_parse_tongue_sole_species_Cyse():
    expected = Species.get("Cyse")
    assert expected is not None
    eq_(parse("Cyse", raise_on_error=True), expected)


def test_parse_tongue_sole_genes():
    for gene_name in ["DAA", "DAB", "DBA", "DBB"]:
        expected = Gene.get("Cyse", gene_name)
        assert expected is not None
        eq_(parse(f"Cyse-{gene_name}", raise_on_error=True), expected)


def test_parse_tongue_sole_alleles():
    for gene_name in ["DAA", "DAB", "DBA", "DBB"]:
        expected = Allele.get("Cyse", gene_name, "01", "01")
        assert expected is not None
        eq_(parse(f"Cyse-{gene_name}*01:01", raise_on_error=True), expected)


def test_parse_orange_spotted_grouper_species_Epco():
    expected = Species.get("Epco")
    assert expected is not None
    eq_(parse("Epco", raise_on_error=True), expected)


def test_parse_orange_spotted_grouper_genes():
    for gene_name in ["DAA", "DAB", "DBB"]:
        expected = Gene.get("Epco", gene_name)
        assert expected is not None
        eq_(parse(f"Epco-{gene_name}", raise_on_error=True), expected)


def test_parse_orange_spotted_grouper_alleles():
    for gene_name in ["DAA", "DAB", "DBB"]:
        expected = Allele.get("Epco", gene_name, "01", "01")
        assert expected is not None
        eq_(parse(f"Epco-{gene_name}*01:01", raise_on_error=True), expected)


def test_parse_brown_trout_species_Satr():
    expected = Species.get("Satr")
    assert expected is not None
    eq_(parse("Satr", raise_on_error=True), expected)


def test_parse_brown_trout_supported_gene_families():
    expected_classes = {"UBA": "Ia", "DAB": "IIa"}
    for gene_name in ["UBA", "DAB"]:
        expected = Gene.get("Satr", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, expected_classes[gene_name])
        eq_(parse(f"Satr-{gene_name}", raise_on_error=True), expected)


def test_do_not_parse_ambiguous_or_unreviewed_fish_strings():
    for s in ["Saal-UEA", "Saal-UBA", "Saal-UGA", "Saal-DAB", "SAAL-UBA", "Satr-DAA"]:
        assert parse(s, raise_on_error=False) is None
