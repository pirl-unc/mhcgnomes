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


def test_parse_zebrafish_class2_genes():
    for gene_name in ["DAA", "DAB"]:
        expected = Gene.get("Dare", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, "IIa")
        eq_(parse(f"Dare-{gene_name}", raise_on_error=True), expected)


def test_parse_zebrafish_additional_class1_genes():
    for gene_name in ["UEA", "UGA"]:
        expected = Gene.get("Dare", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, "Ia")
        eq_(parse(f"Dare-{gene_name}", raise_on_error=True), expected)


def test_parse_medaka_species_Oryl():
    expected = Species.get("Oryl")
    assert expected is not None
    eq_(parse("Oryl", raise_on_error=True), expected)
    eq_(Species.get("Oryzias latipes"), expected)


def test_parse_medaka_genes():
    for gene_name in ["UAA", "UBA", "UGA", "UHA"]:
        expected = Gene.get("Oryl", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, "Ia")
        eq_(parse(f"Oryl-{gene_name}", raise_on_error=True), expected)


def test_medaka_orla_does_not_collide_with_orangutan():
    """Orla should still resolve to orangutan, not medaka."""
    result = Species.get("OrLA")
    assert result is not None
    eq_(result.name, "Pongo sp.")


def test_parse_zebrafish_uma_gene():
    expected = Gene.get("Dare", "UMA")
    assert expected is not None
    eq_(expected.mhc_class, "Ia")
    eq_(parse("Dare-UMA", raise_on_error=True), expected)


def test_parse_zebrafish_mhc1uma_alias():
    expected = Gene.get("Dare", "UMA")
    assert expected is not None
    eq_(parse("Dare-mhc1uma", raise_on_error=True), expected)


def test_parse_zebrafish_zfin_style_aliases():
    examples = [
        ("Dare-mhc1uba", Gene.get("Dare", "UBA")),
        ("Dare-mhc2daa", Gene.get("Dare", "DAA")),
        ("Dare-mhc2dab", Gene.get("Dare", "DAB")),
    ]
    for raw_string, expected in examples:
        assert expected is not None
        eq_(parse(raw_string, raise_on_error=True), expected)


def test_parse_olive_flounder_dab_aliases():
    for alias in ["DAB1", "DAB2", "DAB3", "DAB4", "DAB5", "DAB6"]:
        expected = Gene.get("Paol", "DAB")
        assert expected is not None
        eq_(parse(f"Paol-{alias}", raise_on_error=True), expected)


def test_parse_olive_flounder_dab_alias_alleles():
    for alias in ["DAB1", "DAB3", "DAB6"]:
        expected = Allele.get("Paol", "DAB", "01", "01")
        assert expected is not None
        eq_(parse(f"Paol-{alias}*01:01", raise_on_error=True), expected)


def test_parse_golden_pompano_species_Trov():
    expected = Species.get("Trov")
    assert expected is not None
    eq_(parse("Trov", raise_on_error=True), expected)


def test_parse_golden_pompano_genes():
    expected_classes = {"UBA": "Ia", "DAA": "IIa", "DAB": "IIa"}
    for gene_name in ["UBA", "DAA", "DAB"]:
        expected = Gene.get("Trov", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, expected_classes[gene_name])
        eq_(parse(f"Trov-{gene_name}", raise_on_error=True), expected)


def test_parse_golden_pompano_alleles():
    for gene_name in ["UBA", "DAA", "DAB"]:
        expected = Allele.get("Trov", gene_name, "01", "01")
        assert expected is not None
        eq_(parse(f"Trov-{gene_name}*01:01", raise_on_error=True), expected)


def test_parse_arctic_char_species_Saal():
    expected = Species.get("Saal")
    assert expected is not None
    eq_(parse("Saal", raise_on_error=True), expected)


def test_parse_arctic_char_genes():
    expected_classes = {"UBA": "Ia", "UEA": "Ia", "UGA": "Ia", "DAB": "IIa"}
    for gene_name in ["UBA", "UEA", "UGA", "DAB"]:
        expected = Gene.get("Saal", gene_name)
        assert expected is not None
        eq_(expected.mhc_class, expected_classes[gene_name])
        eq_(parse(f"Saal-{gene_name}", raise_on_error=True), expected)


def test_parse_arctic_char_case_insensitive():
    """SAAL should resolve to Saal (case-insensitive normalization)."""
    expected = Gene.get("Saal", "UBA")
    assert expected is not None
    eq_(parse("SAAL-UBA", raise_on_error=True), expected)


def test_satr_daa_parses_via_common_genes():
    """Satr-DAA now parses because DAA is a vertebrate-wide common gene."""
    result = parse("Satr-DAA", raise_on_error=True)
    assert result is not None
    eq_(result.species.name, "Salmo trutta")
