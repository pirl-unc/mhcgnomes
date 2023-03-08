from mhcgnomes import (
    Parser,
    Allele,
    Pair,
    Mutation,
    Species,
    Haplotype,
    Serotype,
    Gene,
    parse,
)
from mhcgnomes.result_sorting import pick_best_result

def test_parse_lowercase_hla():
    parser = Parser()
    expected = Species.get("HLA")
    assert expected is not None
    result = parser.parse("hla")
    assert result == expected


def test_parse_lowercase_hla_dra_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRA", "01", "01")
    assert expected is not None
    result = parser.parse("hla-dra*01:01")
    assert result == expected


def test_parse_DRB1_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRB1", "01", "01")
    result = parser.parse("DRB1*01:01")
    assert result == expected


def test_parse_lowercase_drb1_01_01():
    parser = Parser()
    expected = Allele.get("HLA", "DRB1", "01", "01")
    result = parser.parse("drb1*01:01")
    assert result == expected


def test_parse_multiple_expect_unique_A0201():
    parser = Parser()
    expected_single = Allele.get("HLA", "A", "02", "01")
    assert expected_single is not None
    expected = [expected_single]
    candidates = parser.parse_multiple_candidates("HLA-A*02:01")
    assert candidates == list(expected)



def test_parse_hla_lowercase_dra_01_01_drb1_01_01():
    parser = Parser()

    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Pair.get(expected_alpha, expected_beta)
    result = parser.parse("hla-dra*01:01/drb1*01:01")
    assert result == expected_result

def test_parse_hla_lowercase_dra_01_01_drb1_01_01_no_default_species():
    parser = Parser()
    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get("HLA", "DRB1", "01", "01")
    expected_result = Pair.get(expected_alpha, expected_beta)
    result = parser.parse("hla-dra*01:01/drb1*01:01", default_species=None)
    assert result == expected_result


def test_parse_multiple_candidates_HLA_DRA_01_01_DRB1_01_01_G86Y_mutant():
    parser = Parser()
    results = parser.parse_multiple_candidates(
        "HLA-DRA*01:01/DRB1*01:01 G86Y mutant")
    expected_mutation = Mutation.get(
        pos=86,
        aa_original="G",
        aa_mutant="Y")
    expected_alpha = Allele.get("HLA", "DRA", "01", "01")
    expected_beta = Allele.get(
        "HLA", "DRB1", "01", "01", mutations=(expected_mutation,))
    expected_result = Pair.get(expected_alpha, expected_beta)
    assert results == [expected_result]

def test_get_haplotypes_for_any_species_BF19():
    parser = Parser()
    results = parser.get_haplotypes_for_any_species("BF19")
    assert len(results) > 0
    result = results[0]
    assert type(result) == Haplotype
    assert result.name == "BF19"

def test_parse_multiple_candidates_BF19_class_II():
    parser = Parser()
    results = parser.parse_multiple_candidates("BF19 class II")
    result = results[0]
    assert type(result) == Haplotype
    assert result.name == "BF19"

def test_parse_haplotype_BF19():
    parser = Parser()
    result = parser.parse_haplotype("BF19")
    assert type(result) == Haplotype
    assert result.name == "BF19"

def test_parse_multiple_candidates_haplotype_BF19():
    parser = Parser()
    results = parser.parse_multiple_candidates("BF19")
    assert len(results) == 1
    result = results[0]
    assert type(result) == Haplotype


def test_parse_multiple_candidates_haplotype_bf19_lowercase():
    parser = Parser()
    results = parser.parse_multiple_candidates("bf19")
    assert len(results) == 1
    result = results[0]
    assert type(result) == Haplotype

def test_parse_allele_or_gene_candidates_DRB5_0108N():
    seq = "DRB5_0108N"
    parser = Parser()
    results = parser.parse_allele_or_gene_candidates(
        species=Species.get("HLA"),
        str_after_species=seq)
    assert results is not None
    assert len(results) > 0
    result = results[0]
    assert type(result) == Allele


def test_parse_DRB5_0108N():
    seq = "DRB5_0108N"
    parser = Parser()
    result = parser.parse(seq)
    assert result is not None
    assert type(result) == Allele


def test_parse_HLA_A2():
    seq = "HLA-A2"
    parser = Parser()
    result = parser.parse(seq)
    assert result is not None
    assert type(result) == Serotype

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
    assert len(results) > 0
    assert any([type(result) is Pair for result in results])

def test_parse_BoLA_DRA_DRB31501():
    parser = Parser()
    result = parser.parse("BoLA-DRA-DRB31501")
    assert result is not None
    assert type(result) is Pair, "Expected Class2Pair but got: %s" % (result,)

def test_parse_H2K():
    parse_fns = [parse, Parser().parse]
    for fn in parse_fns:
        result = fn("H2K")
        assert result is not None

def test_parse_H2_K_valid_types_Gene():
    parse_fns = [parse, Parser().parse]
    for fn in parse_fns:
        result = fn("H2K", required_result_types=[Gene])
        assert type(result) is Gene

def test_parse_H2_K_valid_types_Haplotype():
    parse_fns = [parse, Parser().parse]
    for fn in parse_fns:
        result = fn("H2K", required_result_types=[Haplotype])
        assert type(result) is Haplotype


def test_parse_H2_IAb_I67F_R70Q_T71K_mutant():
    s = "H2-IAb I67F, R70Q, T71K mutant"
    parse_fns = [parse, Parser().parse]
    for fn in parse_fns:
        result = fn(s)
        assert result is not None
        assert type(result) in (Pair, Allele), \
            "Wrong result type: %s" % (result,)
        if type(result) is Allele:
            assert len(result.mutations) == 3
        elif type(result) is Pair:
            assert len(result.beta.mutations) == 3


def test_parse_HLA_DRA_01_01_F54C_mutant_DRB1_01_01():
    s = "HLA-DRA*01:01 F54C mutant/DRB1*01:01"
    parse_fns = [parse, Parser().parse]
    for fn in parse_fns:
        result = fn(s)
        assert result is not None
        assert type(result) is Pair
        assert len(result.alpha.mutations) == 1
        assert len(result.beta.mutations) == 0

def test_raw_strings_from_parse_class_ii():
    alpha = "DPA1*01:05"
    beta = "DPB1*100:01"
    s = "%s-%s" % (alpha, beta)
    parser = Parser()
    result = parser.parse(s)
    assert type(result) == Pair
    assert result.raw_string == s
    assert result.alpha.raw_string.lower() == alpha.lower()
    assert result.beta.raw_string.lower() == beta.lower()

def test_candidates_from_ambiguous_class2_DPA10105_DPB110001():
    s = "DPA10105-DPB110001"
    parser = Parser()
    results = parser.parse_multiple_candidates(s)
    assert len(results) == 1
    eq_(results[0], Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")))


def test_candidates_from_ambiguous_class2_DPB110001():
    s = "DPB110001"
    parser = Parser()
    results = parser.parse_multiple_candidates(s)
    assert len(results) == 2
    assert Allele.get("HLA", "DPB1", "100", "01") in  results


def test_candidates_from_ambiguous_mouse_class2_IAb():
    s = "H-2-IAb"
    parser = Parser()
    results = parser.parse_multiple_candidates(s)
    assert len(results) == 2
    class2 = Pair.get(
        Allele.get("H2", "AA", "b"),
        Allele.get("H2", "AB", "b"))
    assert class2 in results
    gene = Gene.get("H2", "AB")
    assert gene in results
    assert pick_best_result(results) == class2


def test_parse_species_SLA_3_YDY01():
    parser = Parser()
    species, str_after_species = parser.parse_species("SLA-3-YDY01")
    assert species.is_pig
    assert str_after_species.lower() == "3-ydy01"

def test_parse_species_sla_3_ydy01_lower_case():
    parser = Parser()
    species, str_after_species = parser.parse_species("sla-3-ydy01")
    assert species.is_pig
    assert str_after_species.lower() == "3-ydy01"

def test_parse_allele_with_gene_MICA_038():
    parser = Parser()
    allele = parser.parse_allele_with_gene(
        gene=Gene.get("HLA", "MICA"),
        str_after_gene="038")
    assert allele is not None
    assert allele.is_class1
    assert allele.allele_fields == ("038",)


def test_parse_allele_B_27_215N():
    parser = Parser()
    allele = parser.parse_allele_with_gene(
        gene=Gene.get("HLA", "B"),
        str_after_gene="27:215N")
    assert allele.allele_fields == ("27", "215")
    assert allele.annotations == ("N",)

def test_parse_B_27_215N():
    parser = Parser(verbose=True)
    allele = parser.parse("B*27:215N")
    assert allele.allele_fields == ("27", "215")
    assert allele.annotations == ("N",)