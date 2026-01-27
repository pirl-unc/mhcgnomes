from mhcgnomes import Allele, Mutation

from .common import eq_


def test_allele_get_parses_mutation_strings():
    allele = Allele.get("HLA", "A", "02", "01", mutations="N80I")
    expected = Mutation.get(pos=80, aa_original="N", aa_mutant="I")
    eq_(allele.mutations, (expected,))
    assert allele.is_mutant
    assert allele.to_string().endswith("N80I mutant")


def test_mutation_get_preserves_raw_string():
    mutation = Mutation.get(pos=86, aa_original="G", aa_mutant="Y", raw_string="G86Y")
    eq_(mutation.raw_string, "G86Y")
