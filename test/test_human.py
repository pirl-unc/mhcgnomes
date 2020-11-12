from nose.tools import eq_
from mhcgnomes import (
    parse,
    Class2Pair,
    Allele
)


def test_normalized_string_hla_a0201_complete():
    name = "HLA-A*02:01"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_fieldsep():
    name = "HLA-A*0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)


def test_normalized_string_hla_a0201_no_species_no_star_no_fieldsep():
    name = "A0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_star_no_fieldsep():
    name = "HLA-A0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_fieldsep_lowercase():
    name = "hla-a*0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_species_no_fieldsep_lowercase():
    name = "a*0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_species_lowercase():
    name = "a*02:01"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_species_no_star_no_fieldsep_lowercase():
    name = "a0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_species_no_fieldsep():
    name = "A*0201"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)

def test_normalized_string_hla_a0201_no_species():
    name = "A*02:01"
    expected = "HLA-A*02:01"
    eq_(parse(name).to_string(), expected)


hla_02_01_names = [
    "HLA-A*02:01",
    "HLA-A*0201",
    "A*02:01",
    "A*0201",
    "HLA-A02:01",
    # no gene sep
    "HLA-A0201",
    "A0201",
    # lower case
    "hla-a*0201",
    "a*0201",
    "a*02:01",
    "a0201"
]

def test_hla_short_names():
    expected = "A0201"
    for name in hla_02_01_names:
        result = parse(name).compact_string()
        eq_(result, expected)


def test_hla_A2_serotype():
    eq_(parse("A2").compact_string(), "A2")
    eq_(parse("A2").to_string(), "HLA-A2")

    eq_(parse("HLA-A2").compact_string(), "A2")
    eq_(parse("HLA-A2").to_string(), "HLA-A2")


def test_hla_with_3_digit_allele_code():
    # B*15:120
    eq_(parse("HLA-B*15:120").to_string(), "HLA-B*15:120")
    eq_(parse("HLA-B*15:120").compact_string(), "B15120")
    eq_(parse("B15120").to_string(), "HLA-B*15:120")
    eq_(parse("B15120").compact_string(), "B15120")

    # A*02*123
    eq_(parse("HLA-A*02:123").to_string(), "HLA-A*02:123")
    eq_(parse("HLA-A*02:123").compact_string(), "A02123")
    eq_(parse("A02123").to_string(), "HLA-A*02:123")
    eq_(parse("A02123").compact_string(), "A02123")



def test_A_02_01_01_01():
    result = parse("A*02:01:01:01")
    eq_(result.species_prefix, "HLA")
    eq_(result.gene_name, "A")
    eq_(result.allele_fields[0], "02")
    eq_(result.allele_fields[1], "01")
    eq_(result.allele_fields[2], "01")
    eq_(result.allele_fields[3], "01")


def test_parse_human_class2_DRB1_01_02():
    expected = Class2Pair.get(
        Allele.get("HLA", "DRA", "01", "01"),
        Allele.get("HLA", "DRB1", "01", "02"),
    )
    for name in ["DRB1_0102",
                 "DRB101:02",
                 "HLA-DRB1_0102",
                 "DRB10102",
                 "DRB1*0102",
                 "HLA-DRB1*0102",
                 "HLA-DRB1*01:02",
                 "DRB0102"]:
        parse_result = parse(
            name,
            infer_class2_pairing=True)
        eq_(parse_result, expected)


def test_normalized_string_human_class2_DRB1_01_02():
    expected = "HLA-DRA*01:01-DRB1*01:02"
    for name in ["DRB1_0102",
                 "DRB101:02",
                 "HLA-DRB1_0102",
                 "DRB10102",
                 "DRB1*0102",
                 "HLA-DRB1*0102",
                 "HLA-DRB1*01:02",
                 "DRB0102"]:
        eq_(parse(name, infer_class2_pairing=True).to_string(), expected)


def test_compact_string_string_human_class2_DRB1_01_02():
    expected_compact = "DRB1*0102"
    for name in ["DRB1_0102",
                 "DRB101:02",
                 "HLA-DRB1_0102",
                 "DRB10102",
                 "DRB1*0102",
                 "HLA-DRB1*0102",
                 "HLA-DRB1*01:02",
                 "DRB0102"]:
        eq_(parse(name).compact_string(), expected_compact)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_upper_compact():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "DPA10105-DPB110001"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_full_syntax_hyphens():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "HLA-DPA1*01:05-DPB1*100:01"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_full_syntax_hyphens_lower():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "hla-dpa1*0105-dpb1*10001"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_no_hla_lower_no_colons():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "dpa1*0105-dpb1*10001"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_full_syntax_slash():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "HLA-DPA1*01:05/DPB1*100:01"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01_compact_slash():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    s = "DPA10105/DPB110001"
    eq_(parse(s, infer_class2_pairing=True), expected)

def test_parse_all_parameters_true_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01():
    expected = Class2Pair.get(
        Allele.get("HLA", "DPA1", "01", "05"),
        Allele.get("HLA", "DPB1", "100", "01")
    )
    for name in ["DPA10105-DPB110001",
                 "HLA-DPA1*01:05-DPB1*100:01",
                 "hla-dpa1*0105-dpb1*10001",
                 "dpa1*0105-dpb1*10001",
                 "HLA-DPA1*01:05/DPB1*100:01",
                 "DPA10105/DPB110001"]:
        parse_result = parse(
            name,
            map_allele_aliases=True,
            infer_class2_pairing=True)
        eq_(parse_result, expected)

def test_normalize_string_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01():
    expected = "HLA-DPA1*01:05-DPB1*100:01"
    for name in ["DPA10105-DPB110001",
                 "HLA-DPA1*01:05-DPB1*100:01",
                 "hla-dpa1*0105-dpb1*10001",
                 "dpa1*0105-dpb1*10001",
                 "HLA-DPA1*01:05/DPB1*100:01",
                 "DPA10105/DPB110001"]:
        eq_(parse(name, infer_class2_pairing=True).to_string(), expected)


def test_compact_string_human_class2_alpha_beta_DPA1_01_05_DPB1_100_01():
    expected_compact = "DPA1*0105-DPB1*10001"
    for name in ["DPA10105-DPB110001",
                 "HLA-DPA1*01:05-DPB1*100:01",
                 "hla-dpa1*0105-dpb1*10001",
                 "dpa1*0105-dpb1*10001",
                 "HLA-DPA1*01:05/DPB1*100:01",
                 "DPA10105/DPB110001"]:
        eq_(parse(name, infer_class2_pairing=True).compact_string(), expected_compact)


def test_alpha_chain_inference_DP():
    # example of common DP haplotype from wikipedia article on HLA-DP
    just_beta = "HLA-DPB1*04:01"
    expected = "HLA-DPA1*01:03-DPB1*04:01"
    eq_(parse(just_beta, infer_class2_pairing=True).to_string(), expected)
    eq_(parse(just_beta, infer_class2_pairing=False).to_string(), just_beta)


def test_alpha_chain_inference_DQ():
    # example of common DQ haplotype from wikipedia article on HLA-DQ
    just_beta = "HLA-DQB1*06:02"
    expected = "HLA-DQA1*01:02-DQB1*06:02"
    eq_(parse(just_beta, infer_class2_pairing=True).to_string(), expected)
    eq_(parse(just_beta, infer_class2_pairing=False).to_string(), just_beta)

def test_human_class2_pair_with_mutation():
    allele = "HLA-DRA*01:01/DRB1*01:01 G86Y mutant"
    result = parse(allele)
    eq_(type(result), Class2Pair)
    eq_(result.beta.is_mutant, True)


def test_human_class2_beta_with_mutation():
    allele = "DRB1*01:01 G86Y mutant"
    result = parse(allele, infer_class2_pairing=True)
    eq_(type(result), Class2Pair)
    eq_(result.beta.is_mutant, True)

def test_DRB5_0108N():
    allele = "DRB5_0108N"
    result = parse(allele)
    assert result is not None
    eq_(type(result), Allele)
    assert result.annotation_null

def test_DRB5_0108N_with_inferred_alpha():
    allele = "DRB5_0108N"
    result = parse(allele, infer_class2_pairing=True)
    assert result is not None
    eq_(type(result), Class2Pair)
    assert result.annotation_null
