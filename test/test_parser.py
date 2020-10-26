from mhcgnomes import (
    Parser,
    Allele,
    Class2Pair,
    Mutation,
    Species,
    Haplotype,
    Serotype,
    Gene
)
from nose.tools import eq_

def test_parse_lowercase_hla():
    parser = Parser()
    expected = Species.get("HLA")
    assert expected is not None
    result = parser.parse("hla")
    eq_(result, expected)


def test_parse_lowercase_hla_dra_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRA", "01", "01")
    assert expected is not None
    result = parser.parse("hla-dra*01:01")
    eq_(result, expected)


def test_parse_DRB1_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRB1", "01", "01")
    result = parser.parse("DRB1*01:01")
    eq_(result, expected)


def test_parse_lowercase_drb1_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRB1", "01", "01")
    result = parser.parse("drb1*01:01")
    eq_(result, expected)



def test_parse_multiple_expect_unique_A0201():
    parser = Parser()
    expected_single = Allele.get("HLA", "A", "02", "01")
    assert expected_single is not None
    expected = [expected_single]
    candidates = parser.parse_multiple_candidates("HLA-A*02:01")
    eq_(candidates, list(expected))


def test_parse_class2_pair_with_slash_sep_HLA_DRA_01_01_DRB1_01_01():
    parser = Parser()

    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Class2Pair.get(expected_alpha, expected_beta)

    result = parser.parse_class2_pair_with_slash_sep("HLA-DRA*01:01/DRB1*01:01")
    eq_(result, expected_result)


def test_parse_hla_lowercase_dra_01_01_drb1_01_01():
    parser = Parser()

    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Class2Pair.get(expected_alpha, expected_beta)
    result = parser.parse("hla-dra*01:01/drb1*01:01")
    eq_(result, expected_result)

def test_parse_hla_lowercase_dra_01_01_drb1_01_01_no_default_species():
    parser = Parser()
    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Class2Pair.get(expected_alpha, expected_beta)
    result = parser.parse("hla-dra*01:01/drb1*01:01", default_species=None)
    eq_(result, expected_result)

def test_parse_class2_pair_with_slash_sep_lowercase_hla_dra_01_01_drb1_01_01():
    parser = Parser()

    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Class2Pair.get(expected_alpha, expected_beta)
    result = parser.parse_class2_pair_with_slash_sep("hla-dra*01:01/drb1*01:01")
    eq_(result, expected_result)

def test_parse_with_interior_whitespace_HLA_DRA_01_01_DRB1_01_01_G86Y_mutant():
    parser = Parser()
    result = parser.parse_with_interior_whitespace(
        "HLA-DRA*01:01/DRB1*01:01 G86Y mutant")
    expected_mutation = Mutation.get(
        pos=86,
        aa_original="G",
        aa_mutant="Y")
    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get(
        "HLA", "DRB1", "01", "01", mutations=(expected_mutation,))
    expected_result = Class2Pair.get(expected_alpha, expected_beta)
    eq_(result, expected_result)

def test_get_haplotypes_for_any_species_BF19():
    parser = Parser()
    results = parser.get_haplotypes_for_any_species("BF19")
    assert len(results) > 0
    result = results[0]
    eq_(type(result), Haplotype)
    eq_(result.name, "BF19")

def test_parse_with_interior_whitespace_BF19_class_II():
    parser = Parser()
    result = parser.parse_with_interior_whitespace("BF19 class II")
    eq_(type(result), Haplotype)
    eq_(result.name, "BF19")

def test_parse_haplotype_BF19():
    parser = Parser()
    result = parser.parse_haplotype("BF19")
    eq_(type(result), Haplotype)
    eq_(result.name, "BF19")

def test_parse_multiple_candidates_haplotype_BF19():
    parser = Parser()
    results = parser.parse_multiple_candidates("BF19")
    assert len(results) == 1
    result = results[0]
    eq_(type(result), Haplotype)


def test_parse_multiple_candidates_haplotype_bf19_lowercase():
    parser = Parser()
    results = parser.parse_multiple_candidates("bf19")
    assert len(results) == 1
    result = results[0]
    eq_(type(result), Haplotype)

def test_parse_allele_or_gene_candidates_DRB5_0108N():
    seq = "DRB5_0108N"
    parser = Parser()
    results = parser.parse_allele_or_gene_candidates(
        species=Species.get("HLA"),
        str_after_species=seq)
    assert results is not None
    assert len(results) > 0
    result = results[0]
    eq_(type(result), Allele)


def test_parse_DRB5_0108N():
    seq = "DRB5_0108N"
    parser = Parser()
    result = parser.parse(seq)
    print(result)
    assert result is not None
    eq_(type(result), Allele)


def test_parse_HLA_A2():
    seq = "HLA-A2"
    parser = Parser()
    result = parser.parse(seq)
    print(result)
    assert result is not None
    eq_(type(result), Serotype)

def test_parse_multiple_candidates_A2():
    parser = Parser()
    results = parser.parse_multiple_candidates("A2")
    assert len(results) > 0
    assert any([type(result) is Serotype for result in results])

def test_parse_allele_or_gene_candidates_A2():
    parser = Parser()
    results = parser.parse_allele_or_gene_candidates(
        species=Species.get("HLA"),
        str_after_species="A2")
    assert len(results) == 0, "Didn't expect any result but got %s" % (
        results,)

def test_parse_parse_allele_or_gene_candidates_BF2():
    parser = Parser()
    results = parser.parse_allele_or_gene_candidates(
        species=Species.get("chicken"),
        str_after_species="BF2")
    assert len(results) == 1
    result = results[0]
    assert result is not None
    assert type(result) is Gene, result


def test_parse_parse_BF2():
    parser = Parser()
    result = parser.parse("BF2")
    assert result is not None
    assert type(result) is Gene, result

def test_parse_multiple_candidates_BoLA_DRA_DRB31501():
    parser = Parser()
    results = parser.parse_multiple_candidates("BoLA-DRA-DRB31501")
    print(results)
    assert len(results) > 0
    assert any([type(result) is Class2Pair for result in results])

def test_parse_BoLA_DRA_DRB31501():
    parser = Parser()
    result = parser.parse("BoLA-DRA-DRB31501")
    assert result is not None
    assert type(result) is Class2Pair, "Expected Class2Pair but got: %s" % (result,)