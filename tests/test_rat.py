import pytest

from mhcgnomes import Allele, Class2Locus, Gene, Haplotype, Pair, Species, parse

from .common import eq_


def test_parse_RT1():
    species = parse("RT1")
    eq_(type(species), Species)
    eq_(species.prefix, "RT1")


def test_Species_get_RT1():
    species = Species.get("RT1")
    eq_(type(species), Species)
    eq_(species.prefix, "RT1")


def test_parse_Rano():
    species = parse("Rano")
    eq_(type(species), Species)
    eq_(species.prefix, "Rano")


def test_Species_get_Rano():
    species = Species.get("Rano")
    eq_(type(species), Species)
    eq_(species.prefix, "Rano")


def test_rat_class1_allele_Bbu():
    eq_(parse("RT1-Bb*u"), Allele.get("RT1", "Bb", "u"))


def test_rat_class1_allele_Bbu_no_star():
    eq_(parse("RT1-Bbu"), Allele.get("RT1", "Bb", "u"))


def test_rat_class1_allele_Db1a():
    eq_(parse("RT1-Db1*a"), Allele.get("RT1", "Db1", "a"))


def test_rat_class1_allele_Db1a_no_star():
    eq_(parse("RT1-Db1a"), Allele.get("RT1", "Db1", "a"))


def test_rat_class1_allele_DMaa():
    eq_(parse("RT1-DMa*a"), Allele.get("RT1", "DMA", "a"))


def test_rat_class1_allele_DMaa_no_star():
    eq_(parse("RT1-DMAa"), Allele.get("RT1", "DMA", "a"))


def test_rat_class1_allele_95f():
    eq_(parse("RT1-9.5*f"), Allele.get("RT1", "9.5", "f"))


def test_rat_class1_allele_95f_no_star():
    eq_(parse("RT1-9.5f"), Allele.get("RT1", "9.5", "f"))


def test_rat_class1_allele_M3_1_av1():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    eq_(parse("RT1-M3-1*av1"), expected)


def test_rat_class1_allele_M3_1_av1_no_star():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    eq_(parse("RT1-M3-1av1"), expected)


@pytest.mark.parametrize(
    "raw,expected_pair,expected_haplotype",
    [
        ("RT1-Bl", "RT1-Ba*l/Bb*l", "RT1-B-l"),
        ("RT1-B-l", "RT1-Ba*l/Bb*l", "RT1-B-l"),
        ("RT1-Bu", "RT1-Ba*u/Bb*u", "RT1-B-u"),
        ("RT1-Bn", "RT1-Ba*n/Bb*n", "RT1-B-n"),
        ("RT1-Bk", "RT1-Ba*k/Bb*k", "RT1-B-k"),
        ("RT1-Bc", "RT1-Ba*c/Bb*c", "RT1-B-c"),
        ("RT1-Bd", "RT1-Ba*d/Bb*d", "RT1-B-d"),
        ("RT1-Bf", "RT1-Ba*f/Bb*f", "RT1-B-f"),
        ("RT1-Bh", "RT1-Ba*h/Bb*h", "RT1-B-h"),
        ("RT1-Dl", "RT1-Da*l/Db1*l", "RT1-D-l"),
        ("RT1-D-l", "RT1-Da*l/Db1*l", "RT1-D-l"),
        ("RT1-Du", "RT1-Da*u/Db1*u", "RT1-D-u"),
        ("RT1-Dn", "RT1-Da*n/Db1*n", "RT1-D-n"),
        ("RT1-Dk", "RT1-Da*k/Db1*k", "RT1-D-k"),
        ("RT1-Dc", "RT1-Da*c/Db1*c", "RT1-D-c"),
        ("RT1-Dd", "RT1-Da*d/Db1*d", "RT1-D-d"),
        ("RT1-Df", "RT1-Da*f/Db1*f", "RT1-D-f"),
        ("RT1-Dh", "RT1-Da*h/Db1*h", "RT1-D-h"),
    ],
)
def test_rt1_class2_locus_haplotype_symmetry(raw, expected_pair, expected_haplotype):
    pair = parse(raw, raise_on_error=True)
    assert type(pair) is Pair
    eq_(pair.to_string(), expected_pair)
    eq_(pair.mhc_class, "IIa")

    hap = parse(raw, collapse_singleton_haplotypes=False, raise_on_error=True)
    assert type(hap) is Haplotype
    eq_(hap.to_string(), expected_haplotype)
    eq_(hap.mhc_class, "IIa")


@pytest.mark.parametrize("raw", ["RT1-B1l", "RT1-B-1l", "RT1-D1u", "RT1-D-1u"])
def test_rt1_invalid_numbered_locus_haplotype_rejected(raw):
    assert parse(raw, raise_on_error=False) is None


def test_rt1_class2_locus_vs_lowercase_haplotype():
    for raw, locus_name in [("RT1-B", "B"), ("RT1-D", "D"), ("RT1.D", "D"), ("RT1-H", "H")]:
        res = parse(raw, raise_on_error=True)
        assert type(res) is Class2Locus
        eq_(res.name, locus_name)

    for raw, hap_name in [("RT1-b", "b"), ("RT1-d", "d"), ("RT1-h", "h")]:
        res = parse(raw, raise_on_error=True)
        assert type(res) is Haplotype
        eq_(res.name, hap_name)
        assert len(res.alleles) == 4

    # Gene names/aliases at B/D loci remain Gene rather than splitting into locus+haplotype,
    # while explicit hyphenated locus-haplotype spellings (RT1-D-b) still parse as Pair/Haplotype.
    eq_(parse("RT1-Ba", raise_on_error=True), Gene.get("RT1", "Ba"))
    eq_(parse("RT1-Bb", raise_on_error=True), Gene.get("RT1", "Bb"))
    eq_(parse("RT1-Da", raise_on_error=True), Gene.get("RT1", "Da"))
    eq_(parse("RT1-Db", raise_on_error=True), Gene.get("RT1", "Db1"))
    eq_(parse("RT1-A", raise_on_error=True), Gene.get("RT1", "A"))
    eq_(parse("RT1-D-b", raise_on_error=True).to_string(), "RT1-Da*b/Db1*b")


def test_rt1_class2_chain_extraction_and_curated_haplotypes():
    eq_(parse("RT1-Bl alpha", raise_on_error=True), Allele.get("RT1", "Ba", "l"))
    eq_(parse("RT1-Bl beta", raise_on_error=True), Allele.get("RT1", "Bb", "l"))
    eq_(parse("RT1-Du alpha", raise_on_error=True), Allele.get("RT1", "Da", "u"))
    eq_(parse("RT1-Du beta", raise_on_error=True), Allele.get("RT1", "Db1", "u"))

    hap_n = parse("RT1-n", raise_on_error=True)
    assert type(hap_n) is Haplotype
    eq_(
        {a.to_string() for a in hap_n.alleles},
        {
            "RT1-A1*n",
            "RT1-A2*n",
            "RT1-A3*n",
            "RT1-Ba*n",
            "RT1-Bb*n",
            "RT1-Da*n",
            "RT1-Db1*n",
        },
    )

    hap_av1 = parse("RT1-av1", raise_on_error=True)
    assert type(hap_av1) is Haplotype
    eq_(
        {a.to_string() for a in hap_av1.alleles},
        {"RT1-A1*a", "RT1-Ba*a", "RT1-Bb*a", "RT1-Da*a", "RT1-Db1*a"},
    )


"""
def test_RT1_Db_A_weird_uniprot_name():
    seq = "Class II RT1.D(A) beta chain"
    expected = Allele.get("RT1", "Db", "a")
    assert expected is not None
    eq_(parse(seq), expected)
"""
