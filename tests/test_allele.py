from mhcgnomes import Allele, parse

from .common import eq_


def test_allele_get_A0201():
    allele = Allele.get("HLA", "A", "02", "01")
    assert allele is not None
    assert type(allele) is Allele
    eq_(allele.species_prefix, "HLA")
    eq_(allele.gene_name, "A")
    eq_(list(allele.allele_fields), ["02", "01"])
    eq_(allele.mhc_class, "Ia")


def test_restrict_num_allele_fields_A02010101():
    allele_eight_digit = Allele.get("HLA", "A", "02", "01", "01", "01")
    assert allele_eight_digit is not None
    assert type(allele_eight_digit) is Allele
    eq_(allele_eight_digit.num_allele_fields, 4)
    allele_four_digit = allele_eight_digit.restrict_allele_fields(2)
    eq_(allele_four_digit.num_allele_fields, 2)


def test_no_annotations():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_null():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="N")
    assert allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_cytosolic():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="C")
    assert not allele.annotation_null
    assert allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_secreted():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="S")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_questionable():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Q")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_group():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="G")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_splice_variant():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Sp")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert allele.annotation_splice_variant


def test_annotation_pseudogene():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Ps")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


# ---- Field width normalization tests ----


def test_normalize_single_digit_to_two():
    """Single-digit fields are zero-padded to 2 digits for standard HLA genes."""
    allele = parse("A*2:1")
    eq_(list(allele.allele_fields), ["02", "01"])


def test_normalize_already_two_digit_unchanged():
    """Two-digit fields are not changed."""
    allele = parse("A*02:01")
    eq_(list(allele.allele_fields), ["02", "01"])


def test_normalize_three_digit_preserved():
    """Three-digit fields wider than the minimum are never truncated."""
    allele = parse("DPB1*105:01")
    eq_(list(allele.allele_fields), ["105", "01"])


def test_normalize_mica_three_digit():
    """MICA uses 3-digit minimum for first field."""
    allele = parse("MICA*01")
    eq_(list(allele.allele_fields), ["001"])


def test_normalize_mica_already_three_digit():
    """MICA with already 3-digit first field is unchanged."""
    allele = parse("MICA*002:01:01")
    eq_(list(allele.allele_fields), ["002", "01", "01"])


def test_normalize_equality():
    """Alleles with different input widths compare equal after normalization."""
    a1 = parse("A*2:1")
    a2 = parse("A*02:01")
    assert a1 == a2
    assert hash(a1) == hash(a2)


def test_normalize_equality_mica():
    """MICA alleles with different input widths compare equal."""
    a1 = parse("MICA*01")
    a2 = parse("MICA*001")
    assert a1 == a2


def test_normalize_to_string():
    """Normalized alleles produce canonical to_string output."""
    allele = parse("A*2:1")
    eq_(allele.to_string(), "HLA-A*02:01")


def test_normalize_off():
    """normalize_fields=False preserves original widths."""
    allele = Allele.get("HLA", "A", "2", "1", normalize_fields=False)
    eq_(list(allele.allele_fields), ["2", "1"])


def test_normalize_factory_get_with_gene():
    """get_with_gene also normalizes."""
    from mhcgnomes import Gene

    gene = Gene.get("HLA", "A")
    allele = Allele.get_with_gene(gene, ["2", "1"])
    eq_(list(allele.allele_fields), ["02", "01"])
