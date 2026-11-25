"""Regression tests for core Result, Pair, Haplotype, and function_api bugs."""

import pytest

from mhcgnomes import (
    Allele,
    AlleleWithoutGene,
    AmbiguousAlleles,
    Class2Locus,
    Haplotype,
    Pair,
    ParseError,
    parse,
    parse_gene_class,
)

from .common import eq_


def test_allele_restrict_allele_fields_drops_annotations_and_mutations_at_same_width():
    annotated = parse("HLA-A*02:01N", raise_on_error=True)
    stripped_annot = annotated.restrict_allele_fields(2, drop_annotations=True)
    eq_(stripped_annot.annotations, ())
    eq_(stripped_annot.to_string(), "HLA-A*02:01")
    # Default drop_annotations=False preserves annotations and returns self.
    assert annotated.restrict_allele_fields(2) is annotated

    mutated = parse("HLA-A*02:01 G86Y mutant", raise_on_error=True)
    stripped_mut = mutated.restrict_allele_fields(2, drop_mutations=True)
    assert not stripped_mut.is_mutant
    eq_(stripped_mut.mutations, ())
    eq_(stripped_mut.to_string(), "HLA-A*02:01")
    assert mutated.restrict_allele_fields(2) is mutated


def test_pair_is_mutant_to_record_and_drop_mutations():
    pair = parse("HLA-DRA*01:01/DRB1*01:01 beta G86Y mutant", raise_on_error=True)
    assert isinstance(pair, Pair)
    assert pair.is_mutant
    assert pair.to_record()["is_mutant"] is True

    stripped = pair.restrict_allele_fields(2, drop_mutations=True)
    assert isinstance(stripped, Pair)
    assert not stripped.is_mutant
    assert stripped.to_record()["is_mutant"] is False
    eq_(stripped.to_string(), "HLA-DRA*01:01/DRB1*01:01")

    plain = parse("HLA-DRA*01:01/DRB1*01:01", raise_on_error=True)
    assert not plain.is_mutant
    assert plain.to_record()["is_mutant"] is False


def test_allele_without_gene_and_ambiguous_alleles_restrict_allele_fields():
    awg = parse("BoLA-D18.4", raise_on_error=True)
    assert isinstance(awg, AlleleWithoutGene)
    eq_(awg.restrict_allele_fields(2, drop_annotations=True, drop_mutations=True), awg)

    ambiguous = parse("SahaI*74/88", max_allele_fields=2, raise_on_error=True)
    assert isinstance(ambiguous, AmbiguousAlleles)
    restricted = ambiguous.restrict_allele_fields(2, drop_annotations=True, drop_mutations=True)
    eq_(restricted, ambiguous)


def test_collection_restrict_allele_fields_deduplicates():
    sero = parse("HLA-A2", raise_on_error=True)
    restricted = sero.restrict_allele_fields(1)
    eq_(len(restricted.alleles), len(set(restricted.alleles)))
    eq_(restricted.alleles, (Allele.get("HLA", "A", "02"),))


def test_haplotype_compact_string_accepts_use_old_species_prefix():
    hap = parse("H2-b", raise_on_error=True)
    assert isinstance(hap, Haplotype)
    eq_(hap.compact_string(include_species=False, use_old_species_prefix=False), "b")
    eq_(hap.compact_string(include_species=True, use_old_species_prefix=False), "H2-b")
    eq_(
        hap.compact_string(include_species=True, use_old_species_prefix=True),
        hap.to_string(include_species=True, use_old_species_prefix=True),
    )


def test_haplotype_restrictions_preserve_parent_haplotypes():
    crossed = parse("H2-b/d", raise_on_error=True)
    assert isinstance(crossed, Haplotype)
    assert crossed.parent_haplotypes is not None
    eq_(len(crossed.parent_haplotypes), 2)

    class1 = parse("H2-b/d class I", raise_on_error=True)
    assert isinstance(class1, Haplotype)
    eq_(class1.parent_haplotypes, crossed.parent_haplotypes)

    ia_locus = parse("H2-IA", raise_on_error=True)
    assert isinstance(ia_locus, Class2Locus)
    eq_(ia_locus.name, "A")
    locus_restricted = crossed.restrict_class2_locus(ia_locus)
    eq_(locus_restricted.parent_haplotypes, crossed.parent_haplotypes)
    eq_(locus_restricted.locus_restriction, ia_locus)


def test_require_explicit_species_not_bypassed_by_context_only_gene():
    # Bare "N" has no species prefix in the input, so require_explicit_species=True
    # must reject it even when species="Homo sapiens" is supplied.
    assert (
        parse("N", species="Homo sapiens", require_explicit_species=True, raise_on_error=False)
        is None
    )
    with pytest.raises(ParseError):
        parse("N", species="Homo sapiens", require_explicit_species=True, raise_on_error=True)

    # Without require_explicit_species, it resolves and records species_source="default".
    rescued_gene = parse("N", species="Homo sapiens", raise_on_error=True)
    eq_(rescued_gene.to_string(), "HLA-N")
    eq_(rescued_gene.species_source, "default")

    # Context-only species prefix in the input IS explicit.
    rescued_prefix = parse(
        "Orla-UBA", species="Oryzias latipes", require_explicit_species=True, raise_on_error=True
    )
    eq_(rescued_prefix.to_string(), "OryzLati-UBA")
    eq_(rescued_prefix.species_source, "explicit")


def test_species_source_preserved_across_copy_and_ancestor_reparse():
    explicit = parse("HLA-A*02:01:01:01", raise_on_error=True)
    eq_(explicit.species_source, "explicit")
    eq_(explicit.restrict_allele_fields(2).species_source, "explicit")

    reparsed = parse("SLA-1*04:01", species="Sus scrofa", raise_on_error=True)
    eq_(reparsed.species.name, "Sus scrofa")
    eq_(reparsed.species_source, "explicit")


def test_unknown_species_and_mutually_exclusive_default_species_contracts():
    with pytest.raises(ParseError, match="Unknown species"):
        parse("A*02:01", species="Nonexistus fictionalus", raise_on_error=True)

    assert parse("A*02:01", species="Nonexistus fictionalus", raise_on_error=False) is None

    # Passing both species= and non-default default_species= must always raise
    # ValueError, even when species= is unknown or raise_on_error=False.
    with pytest.raises(ValueError):
        parse_gene_class(
            "A*02:01",
            species="Nonexistus fictionalus",
            default_species="H2",
            raise_on_error=False,
        )


def test_haplotype_get_class2_pair_preserves_mhc_class_and_raw_string():
    for raw in ("H2-IAb", "H2-IAd", "H2-IAk", "H2-IAg7", "H2-IEk", "H2-IEd"):
        pair = parse(raw, raise_on_error=True)
        assert isinstance(pair, Pair)
        eq_(pair.mhc_class, "IIa")
        eq_(pair.raw_string, raw)

    hap = parse("H2-IAb", collapse_singleton_haplotypes=False, raise_on_error=True)
    assert isinstance(hap, Haplotype)
    collapsed = hap.get_class2_pair()
    assert isinstance(collapsed, Pair)
    eq_(collapsed.mhc_class, "IIa")
    eq_(collapsed.raw_string, hap.raw_string)


def test_restrict_class2_locus_rejects_non_class2_locus():
    hap = parse("H2-b", raise_on_error=True)
    other_hap = parse("H2-ia", raise_on_error=True)
    assert isinstance(hap, Haplotype)
    assert isinstance(other_hap, Haplotype)

    with pytest.raises(TypeError, match="Expected Class2Locus"):
        hap.restrict_class2_locus(other_hap, raise_on_error=True)
    assert hap.restrict_class2_locus(other_hap, raise_on_error=False) is None


def test_pair_get_computes_common_mhc_class_for_heterogeneous_chains():
    ia = parse("HLA-A*02:01", raise_on_error=True)
    ib = parse("HLA-E*01:01", raise_on_error=True)
    iia = parse("HLA-DRA*01:01", raise_on_error=True)
    iib = parse("HLA-DMB*01:01", raise_on_error=True)
    b2m = parse("HLA-B2M", raise_on_error=True)

    eq_(Pair.get(ia, b2m).mhc_class, "Ia")
    eq_(Pair.get(b2m, ib).mhc_class, "Ib")
    eq_(Pair.get(ia, ib).mhc_class, "I")
    eq_(Pair.get(iia, iib).mhc_class, "II")


def test_h2_ia_locus_alias_vs_lowercase_ia_haplotype():
    for raw in ("H2-IA", "H2-I-A", "H-2-IA", "H-2-I-A"):
        result = parse(raw, raise_on_error=True)
        assert isinstance(result, Class2Locus), f"{raw!r} parsed as {result!r}"
        eq_(result.name, "A")
        eq_(result.to_string(), "H2-A")

    for raw in ("IA", "I-A"):
        result = parse(raw, species="H2", raise_on_error=True)
        assert isinstance(result, Class2Locus), f"{raw!r} parsed as {result!r}"
        eq_(result.name, "A")

    # Lowercase H2-ia and explicit "haplotype" stay Haplotype('ia').
    for raw in ("H2-ia", "H2-ia haplotype", "H2-IA haplotype"):
        result = parse(raw, raise_on_error=True)
        assert isinstance(result, Haplotype), f"{raw!r} parsed as {result!r}"
        eq_(result.name, "ia")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("HLA\u2010A*02:01", "HLA-A*02:01"),  # HYPHEN
        ("HLA\u2011A*02:01", "HLA-A*02:01"),  # NON-BREAKING HYPHEN
        ("HLA\u2012A*02:01", "HLA-A*02:01"),  # FIGURE DASH
        ("HLA\u2212A*02:01", "HLA-A*02:01"),  # MINUS SIGN
        ("H\u20112\u2011Kb", "H2-K*b"),
        ("\u201cHLA-A*02:01\u201d", "HLA-A*02:01"),  # curly double quotes
        ("\u2018HLA-A*02:01\u2019", "HLA-A*02:01"),  # curly single quotes
    ],
)
def test_unicode_hyphens_and_curly_quotes_parse(raw, expected):
    result = parse(raw, raise_on_error=True)
    eq_(result.to_string(), expected)
