import pytest

from mhcgnomes import Gene, ParseError, infer_mhc_class, parse, parse_gene_class

from .common import eq_


def test_infer_mhc_class_from_species_aware_suffix():
    eq_(infer_mhc_class("F10", species="Pogona vitticeps"), "I")
    eq_(infer_mhc_class("Povi-F10"), "I")


@pytest.mark.parametrize(
    "raw_string, expected_class, expected_chain",
    [
        ("RT1.A(u)", "Ia", "alpha"),
        ("RT1.A1(f)", "Ia", "alpha"),
        ("RT1.B", "II", None),
        ("RT1.D", "II", None),
        ("RT1-Ba", "IIa", "alpha"),
        ("RT1-DOa", "IIb", "alpha"),
        ("RT1-DOb", "IIb", "beta"),
        ("H2-Oa", "IIb", "alpha"),
        ("H2-Ob", "IIb", "beta"),
        ("I-A-beta", "IIa", "beta"),
        ("MHC II H2-IE-beta", "IIa", "beta"),
        ("rt1-El", "I", "alpha"),
        ("rt1-Eg", "I", "alpha"),
    ],
)
def test_infer_mhc_class_handles_rt1_and_h2_edge_cases(raw_string, expected_class, expected_chain):
    eq_(infer_mhc_class(raw_string), expected_class)
    result = parse_gene_class(raw_string)
    eq_(result.mhc_class, expected_class)
    eq_(result.chain, expected_chain)


def test_parse_gene_class_preserves_strict_parse_for_canonical_gene():
    result = parse_gene_class("PogoVitt-DRA")
    eq_(result.species.name, "Pogona vitticeps")
    eq_(result.gene_name, "DRA")
    eq_(result.mhc_class, "IIa")
    eq_(result.chain, "alpha")
    assert not result.non_mhc
    eq_(result.source, "parsed_gene")


def test_parse_gene_class_heuristically_recovers_f10_with_species_hint():
    result = parse_gene_class("F10", species="Pogona vitticeps")
    eq_(result.species.name, "Pogona vitticeps")
    eq_(result.gene_name, "F10")
    eq_(result.mhc_class, "I")
    eq_(result.chain, "alpha")
    assert not result.non_mhc
    eq_(result.source, "heuristic_suffix")


def test_parse_gene_class_heuristically_recovers_dr_1():
    result = parse_gene_class("DR-1", species="Pogona vitticeps")
    eq_(result.gene_name, "DR-1")
    eq_(result.mhc_class, "IIa")
    eq_(result.chain, "alpha")


def test_parse_gene_class_heuristically_recovers_drb_range():
    result = parse_gene_class("DRB1-4", species="Pipra filicauda")
    eq_(result.gene_name, "DRB1-4")
    eq_(result.mhc_class, "IIa")
    eq_(result.chain, "beta")


def test_parse_gene_class_respects_species_context_for_colliding_prefixes():
    fish = parse_gene_class("Hymo-DAB", species="Hypophthalmichthys molitrix")
    gibbon = parse_gene_class("Hymo-DRB1*04:01", species="Hylobates moloch")
    medaka = parse_gene_class("ORLA-UAA", species="Oryzias latipes")

    eq_(fish.species.name, "Hypophthalmichthys molitrix")
    eq_(fish.gene_name, "DAB")
    eq_(fish.chain, "beta")

    eq_(gibbon.species.name, "Hylobates moloch")
    eq_(gibbon.gene_name, "DRB1")
    eq_(gibbon.chain, "beta")

    eq_(medaka.species.name, "Oryzias latipes")
    eq_(medaka.gene_name, "UAA")
    eq_(medaka.chain, "alpha")


def test_parse_gene_class_marks_known_other_genes_as_non_mhc():
    result = parse_gene_class("Tap1", species="Pogona vitticeps")
    eq_(result.gene_name, "TAP1")
    eq_(result.mhc_class, "other")
    eq_(result.chain, None)
    assert result.non_mhc
    assert result.source in {"parsed_gene", "canonical_gene"}


def test_parse_gene_class_marks_known_non_ontology_helper_gene_as_non_mhc():
    for raw_string, expected_gene in [
        ("Ciita", "CIITA"),
        ("Hm13", "HM13"),
        ("Prr3", "PRR3"),
    ]:
        result = parse_gene_class(raw_string, species="Pogona vitticeps")
        eq_(result.gene_name, expected_gene)
        eq_(result.mhc_class, "other")
        eq_(result.chain, None)
        assert result.non_mhc
        eq_(result.source, "non_mhc_name")


def test_gene_class_info_string_and_record_helpers():
    heuristic = parse_gene_class("F10", species="Pogona vitticeps")
    eq_(heuristic.to_string(), "PogoVitt-F10")
    eq_(heuristic.compact_string(), "F10")
    eq_(heuristic.to_record()["gene_name"], "F10")
    eq_(heuristic.to_record()["mhc_class"], "I")
    eq_(heuristic.to_record()["chain"], "alpha")

    non_mhc = parse_gene_class("Ciita", species="Pogona vitticeps")
    eq_(non_mhc.to_string(include_species=False), "CIITA")
    eq_(non_mhc.to_record()["non_mhc"], True)
    eq_(non_mhc.to_record()["source"], "non_mhc_name")


def test_parse_gene_class_requires_species_context_for_heuristics():
    assert infer_mhc_class("DR-1") is None
    with pytest.raises(ParseError):
        parse_gene_class("DR-1")


def test_parse_remains_conservative_for_gap_report_suffixes():
    for raw in ["Povi-F10", "Miun-E-S", "Gese-DR-1"]:
        assert parse(raw, raise_on_error=False) is None


def test_parse_verbose_mouse_class2_beta_notation():
    result = parse("MHC II H2-IE-beta", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.prefix, "H2")
    eq_(result.name, "EB")
