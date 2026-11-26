import pytest

from mhcgnomes import (
    Allele,
    Class2Locus,
    Gene,
    Haplotype,
    Pair,
    ParseError,
    parse,
)

from .common import eq_


def test_mouse_class1_alleles_H2_Kk():
    H2Kk = Allele.get("H2", "K", "k")

    eq_(parse("H2-Kk"), H2Kk)

    # with a hyphen in "H-2"
    eq_(parse("H-2-Kk"), H2Kk)


def test_mouse_class1_alleles_H2_Db():
    H2Db = Allele.get("H2", "D", "b")

    eq_(parse("H2-Db"), H2Db)

    # with hyphen in "H-2"
    eq_(parse("H-2-Db"), H2Db)


def test_H2_Kd_without_seps():
    eq_(parse("H2Kd"), Allele.get("H2", "K", "d"))


def test_H2_Lq_with_dash_in_species():
    eq_(parse("H-2-Lq"), Allele.get("H2", "L", "q"))


def test_H2_Lq_without_dash_in_species():
    eq_(parse("H2-Lq"), Allele.get("H2", "L", "q"))


def test_mouse_class2_gene():
    # H2-IAb
    gene = Gene.get("H2", "EB2")
    eq_(parse("H2-IEb2"), gene)

    # with hyphen in "H-2"
    eq_(parse("H-2-IEb2"), gene)


def test_parse_H2r():
    haplotype = parse("H2-r")
    assert isinstance(haplotype, Haplotype)
    eq_(haplotype.to_string(), "H2-r")


def test_parse_H2_IE():
    result = parse("H2-IE")
    eq_(type(result), Class2Locus)
    eq_(result.name, "E")


def test_mouse_MR1_weird_uniprot_entry():
    seq = "Major histocompatibility complex class I-related gene protein OS=Mus musculus OX=10090 GN=Mr1 PE=1 SV=2"
    result = parse(seq)
    expected = Gene.get("H2", "MR1")
    eq_(result, expected)


def test_parse_H2_IEd_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=True)
    eq_(type(result), Pair)
    eq_(result.alpha.name, "d")
    eq_(result.beta.name, "d")


def test_parse_H2_IEd_no_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=False)
    eq_(type(result), Haplotype)
    eq_(result.name, "d")
    assert result.locus_restriction is not None


# ---- Mouse class II gene name variants ----


def test_parse_mouse_MHC_II_IE_beta():
    """'mouse MHC II IE-beta' should parse as H2-EB gene."""
    result = parse("mouse MHC II IE-beta")
    assert result is not None, "Failed to parse 'mouse MHC II IE-beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")
    eq_(result.species_prefix, "H2")


def test_parse_MHC_II_I_E_beta():
    """'MHC II I-E beta' should parse as H2-EB gene."""
    result = parse("MHC II I-E beta")
    assert result is not None, "Failed to parse 'MHC II I-E beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_murine_MHC_class_II_I_E_beta():
    """'murine MHC class II I-E beta' should parse as H2-EB gene."""
    result = parse("murine MHC class II I-E beta")
    assert result is not None, "Failed to parse 'murine MHC class II I-E beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")
    eq_(result.species_prefix, "H2")


def test_parse_H2_IE_beta_chain():
    """'H2-IE beta chain' should parse as H2-EB gene."""
    result = parse("H2-IE beta chain")
    assert result is not None, "Failed to parse 'H2-IE beta chain'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_I_E_beta_chain():
    """'I-E beta chain' should parse as H2-EB gene."""
    result = parse("I-E beta chain")
    assert result is not None, "Failed to parse 'I-E beta chain'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_murine_species():
    """'murine' should be recognized as Mus musculus."""
    from mhcgnomes import Species

    species = Species.get("murine")
    assert species is not None
    eq_(species.prefix, "H2")


# ---- Contradictory class markers should fail ----


def test_mouse_MHC_I_IE_beta_fails():
    """IE is class II, so 'mouse MHC I IE-beta' is contradictory and must not parse."""
    with pytest.raises(ParseError):
        parse("mouse MHC I IE-beta")


def test_mouse_MHC_class_I_I_A_alpha_fails():
    """I-A is class II, so 'mouse MHC class I I-A alpha' is contradictory."""
    with pytest.raises(ParseError):
        parse("mouse MHC class I I-A alpha")


def test_mouse_MHC_class_I_I_E_beta_fails():
    """I-E is class II, so 'mouse MHC class I I-E beta' is contradictory."""
    with pytest.raises(ParseError):
        parse("mouse MHC class I I-E beta")


# ---- Bare mouse I-A / I-E nomenclature (#300) ----


@pytest.mark.parametrize(
    "raw, expected_type, expected_str, expected_haplotype_str",
    [
        ("I-Ab", Pair, "H2-AA*b/AB*b", "H2-A-b"),
        ("I-A^b", Pair, "H2-AA*b/AB*b", "H2-A-b"),
        ("IAb", Pair, "H2-AA*b/AB*b", "H2-A-b"),
        ("I-Ad", Pair, "H2-AA*d/AB*d", "H2-A-d"),
        ("I-A^d", Pair, "H2-AA*d/AB*d", "H2-A-d"),
        ("IAd", Pair, "H2-AA*d/AB*d", "H2-A-d"),
        ("I-Ak", Pair, "H2-AA*k/AB*k", "H2-A-k"),
        ("I-A^k", Pair, "H2-AA*k/AB*k", "H2-A-k"),
        ("IAk", Pair, "H2-AA*k/AB*k", "H2-A-k"),
        ("I-Ag7", Pair, "H2-AA*d/AB*g7", "H2-A-g7"),
        ("I-A^g7", Pair, "H2-AA*d/AB*g7", "H2-A-g7"),
        ("IAg7", Pair, "H2-AA*d/AB*g7", "H2-A-g7"),
        ("I-As", Pair, "H2-AA*s/AB*s", "H2-A-s"),
        ("I-Aq", Pair, "H2-AA*q/AB*q", "H2-A-q"),
        ("I-Au", Pair, "H2-AA*u/AB*u", "H2-A-u"),
        ("I-Af", Pair, "H2-AA*f/AB*f", "H2-A-f"),
        ("I-Eb", Allele, "H2-EB*b", "H2-E-b"),
        ("IEb", Allele, "H2-EB*b", "H2-E-b"),
        ("I-Ed", Pair, "H2-EA*d/EB*d", "H2-E-d"),
        ("I-E^d", Pair, "H2-EA*d/EB*d", "H2-E-d"),
        ("IEd", Pair, "H2-EA*d/EB*d", "H2-E-d"),
        ("I-Ek", Pair, "H2-EA*k/EB*k", "H2-E-k"),
        ("I-E^k", Pair, "H2-EA*k/EB*k", "H2-E-k"),
        ("IEk", Pair, "H2-EA*k/EB*k", "H2-E-k"),
    ],
)
def test_bare_mouse_ia_ie_haplotype_molecules(
    raw, expected_type, expected_str, expected_haplotype_str
):
    collapsed = parse(raw)
    assert type(collapsed) is expected_type
    eq_(collapsed.to_string(), expected_str)
    eq_(collapsed.species_prefix, "H2")
    eq_(collapsed.species_source, "inferred")
    assert parse(raw, require_explicit_species=True, raise_on_error=False) is None

    retained = parse(raw, collapse_singleton_haplotypes=False)
    assert type(retained) is Haplotype
    eq_(retained.to_string(), expected_haplotype_str)


@pytest.mark.parametrize(
    "raw, expected_locus",
    [
        ("I-A", "A"),
        ("IA", "A"),
        ("I-E", "E"),
        ("IE", "E"),
    ],
)
def test_bare_mouse_ia_ie_class2_loci(raw, expected_locus):
    result = parse(raw)
    assert type(result) is Class2Locus
    eq_(result.species_prefix, "H2")
    eq_(result.name, expected_locus)


def test_bare_mouse_ia_ie_chain_and_lowercase_haplotype_preserved():
    eq_(parse("I-A alpha"), Gene.get("H2", "AA"))
    eq_(parse("I-A beta"), Gene.get("H2", "AB"))
    eq_(parse("I-E alpha"), Gene.get("H2", "EA"))
    eq_(parse("I-E beta"), Gene.get("H2", "EB"))
    eq_(parse("I-Ab alpha"), Allele.get("H2", "AA", "b"))
    eq_(parse("I-Ab beta"), Allele.get("H2", "AB", "b"))
    eq_(parse("I-Ag7 beta"), Allele.get("H2", "AB", "g7"))
    eq_(parse("I-Ek alpha"), Allele.get("H2", "EA", "k"))
    eq_(parse("I-Ek beta"), Allele.get("H2", "EB", "k"))
    eq_(parse("I-Eb2"), Gene.get("H2", "EB2"))
    eq_(parse("I-Ab", required_result_types=Gene), Gene.get("H2", "AB"))

    # Lowercase "ia" remains Haplotype('ia'), not Class2Locus('A')
    ia_hap = parse("ia")
    assert type(ia_hap) is Haplotype
    eq_(ia_hap.name, "ia")

    # Strict species mismatch is rejected
    assert parse("I-Ab", species="Homo sapiens", raise_on_error=False) is None


@pytest.mark.parametrize(
    "raw, expected_str, expected_haplotype_str",
    [
        ("H-2/IAb", "H2-AA*b/AB*b", "H2-A-b"),
        ("H2/IAb", "H2-AA*b/AB*b", "H2-A-b"),
        ("H-2/IAd", "H2-AA*d/AB*d", "H2-A-d"),
        ("H-2/IAk", "H2-AA*k/AB*k", "H2-A-k"),
        ("H-2/IAq", "H2-AA*q/AB*q", "H2-A-q"),
        ("H-2/IAs", "H2-AA*s/AB*s", "H2-A-s"),
        ("H-2/IAu", "H2-AA*u/AB*u", "H2-A-u"),
        ("H-2/IEd", "H2-EA*d/EB*d", "H2-E-d"),
        ("H-2/IEk", "H2-EA*k/EB*k", "H2-E-k"),
    ],
)
def test_species_slash_separator_h2_class2(raw, expected_str, expected_haplotype_str):
    """Slash directly after an explicit species prefix parses (#295)."""
    result = parse(raw)
    assert type(result) is Pair
    eq_(result.to_string(), expected_str)
    eq_(result.species_source, "explicit")
    assert parse(raw, require_explicit_species=True) == result

    retained = parse(raw, collapse_singleton_haplotypes=False)
    assert type(retained) is Haplotype
    eq_(retained.to_string(), expected_haplotype_str)


@pytest.mark.parametrize(
    "invalid",
    ["/H-2-IAb", "/HLA-A*02:01", "H-2/", "H-2//IAb", "H-2/HLA-A*02:01"],
)
def test_malformed_species_slash_inputs_stay_rejected(invalid):
    assert parse(invalid, raise_on_error=False) is None


@pytest.mark.parametrize(
    "raw, expected_gene, expected_field",
    [
        ("Qa-1b", "T23", "b"),
        ("Qa-1^b", "T23", "b"),
        ("Qa1b", "T23", "b"),
        ("Qa-1*b", "T23", "b"),
        ("Qa-1a", "T23", "a"),
        ("Qa-1^a", "T23", "a"),
        ("Qa-1d", "T23", "d"),
        ("Qa-2a", "Q7", "a"),
        ("Qa-2^a", "Q7", "a"),
        ("Qa2b", "Q7", "b"),
        ("T23b", "T23", "b"),
        ("T23^b", "T23", "b"),
    ],
)
def test_bare_mouse_qa1_and_qa2_alleles(raw, expected_gene, expected_field):
    """Bare mouse Qa-1/Qa-2 alleles resolve consistently with H2-prefixed forms (#318)."""
    result = parse(raw)
    assert type(result) is Allele
    eq_(result, Allele.get("H2", expected_gene, expected_field))
    eq_(result.species_source, "inferred")
    assert parse(raw, require_explicit_species=True, raise_on_error=False) is None
    assert parse(raw, species="Homo sapiens", raise_on_error=False) is None


def test_mouse_h2_ab1_aliases_to_ab():
    """H2-Ab1 (MGI:95896) aliases to canonical H2-AB, matching H2-Eb1 -> H2-EB (#323)."""
    eq_(parse("H2-Ab1*b"), Allele.get("H2", "AB", "b"))
    eq_(parse("H2-AB1*b"), Allele.get("H2", "AB", "b"))
    eq_(parse("H2-Ab1*g7"), Allele.get("H2", "AB", "g7"))
    eq_(parse("H2-AA*b/AB1*b"), parse("I-Ab"))
    eq_(parse("H2-Aa*d/Ab1*g7"), parse("I-Ag7"))
    eq_(parse("H2-Eb1*k"), Allele.get("H2", "EB", "k"))


def test_bare_mouse_qa_genes_and_b2m_unaffected():
    eq_(parse("Qa-1"), Gene.get("H2", "T23"))
    eq_(parse("Qa-2"), Gene.get("H2", "Q7"))
    eq_(parse("B2M"), Gene.get("HLA", "B2M"))
