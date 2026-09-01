import pytest

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_


def test_macaque_allele_B_08_02():
    allele_name = "Mamu-B*082:02"
    eq_(parse(allele_name).to_string(), "Mamu-B*082:02")
    eq_(parse(allele_name).compact_string(), "B08202")


def test_macaque_allele_B_007_02():
    # expect 3rd zero in the family "007" to be trimmed in the normalized form
    # of this allele
    allele_name = "Mamu-B*007:02"
    eq_(parse(allele_name).to_string(), "Mamu-B*007:02")
    eq_(parse(allele_name).compact_string(), "B00702")


def test_gelada_species_Thge():
    expected = Species.get("Thge")
    assert expected is not None
    eq_(parse("Thge"), expected)


def test_gelada_gene_Thge_DQA1():
    expected = Gene.get("Thge", "DQA1")
    assert expected is not None
    eq_(parse("Thge-DQA1"), expected)


def test_gelada_allele_Thge_DQA1_25_01():
    expected = Allele.get("Thge", "DQA1", "25", "01")
    assert expected is not None
    eq_(parse("Thge-DQA1*25:01"), expected)


def test_monkey_species_Aoni():
    expected = Species.get("Aoni")
    assert expected is not None
    eq_(parse("Aoni"), expected)


def test_monkey_gene_Aoni_DRB3():
    expected = Gene.get("Aoni", "DRB3")
    assert expected is not None
    eq_(parse("Aoni-DRB3"), expected)


def test_monkey_allele_Aoni_DRB3_06_01():
    expected = Allele.get("Aoni", "DRB3", "06", "01")
    assert expected is not None
    eq_(parse("Aoni-DRB3*06:01"), expected)


def test_Mamu_A7_allele_without_seps():
    s = "Mamu-A70103"
    eq_(parse(s).to_string(), "Mamu-A7*01:03")


def test_parse_saoe_gene_alias_N():
    result = parse("Saoe-N", raise_on_error=True)
    expected = Gene.get("Saoe", "N1")
    assert expected is not None
    eq_(result, expected)


def test_parse_saoe_allele_alias_N_01_01():
    result = parse("Saoe-N*01:01", raise_on_error=True)
    expected = Allele.get("Saoe", "N1", ("01", "01"))
    assert expected is not None
    eq_(result, expected)


def test_parse_maar_gene_alias_A():
    """
    "Maar-A" used to normalize to A1, because Macaca arctoides declared A1 but
    not A and sat outside Macaca sp. Since #123 it is under the genus node and
    inherits A, so it behaves like every other macaque: Mamu-A, Mafa-A and
    Mane-A all stay A. The old answer was the odd one out.
    """
    result = parse("Maar-A", raise_on_error=True)
    eq_(result, Gene.get("Maar", "A"))
    eq_(parse("Mamu-A", raise_on_error=True).name, result.name)


def test_parse_maar_allele_alias_A_01_01():
    """The allele counterpart of the gene test above; see #123."""
    result = parse("Maar-A*01:01", raise_on_error=True)
    eq_(result, Allele.get("Maar", "A", ("01", "01")))
    eq_(result.gene.name, parse("Mamu-A*01:01", raise_on_error=True).gene.name)


NHP_NOVEL_GENE_EXAMPLES = [
    ("Paha-AG*02:01:01:01", "Paha", "AG", ("02", "01", "01", "01")),
    ("Mamu-K*02:01:01:01", "Mamu", "K", ("02", "01", "01", "01")),
    ("Paha-J*01:01:01:01", "Paha", "J", ("01", "01", "01", "01")),
    ("Paha-K*01:01:01:01", "Paha", "K", ("01", "01", "01", "01")),
    ("Paan-AG*02:01:01:01", "Paan", "AG", ("02", "01", "01", "01")),
    ("Paan-J*01:01:01:01", "Paan", "J", ("01", "01", "01", "01")),
    ("Paan-K*01:01:01:01", "Paan", "K", ("01", "01", "01", "01")),
]


NHP_PSEUDOGENE_ALLELES = [
    ("Saoe-G*03:12ps", "Saoe", "G", ("03", "12")),
    ("Saoe-G*03:13ps", "Saoe", "G", ("03", "13")),
    ("Saoe-G*03:14ps", "Saoe", "G", ("03", "14")),
    ("Saoe-G*03:16ps", "Saoe", "G", ("03", "16")),
    ("Saoe-G*03:17ps", "Saoe", "G", ("03", "17")),
    ("Saoe-G*03:18ps", "Saoe", "G", ("03", "18")),
    ("Saoe-G*03:19ps", "Saoe", "G", ("03", "19")),
    ("Saoe-G*03:20ps", "Saoe", "G", ("03", "20")),
    ("Caja-B2*01:01ps", "Caja", "B2", ("01", "01")),
    ("Caja-B5*01:01ps", "Caja", "B5", ("01", "01")),
    ("Caja-B8*01:01ps", "Caja", "B8", ("01", "01")),
    ("Caja-B9*01:01ps", "Caja", "B9", ("01", "01")),
]


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,_fields",
    NHP_NOVEL_GENE_EXAMPLES,
)
def test_nhp_novel_gene_lookup(allele_name, species_prefix, gene_name, _fields):
    gene = Gene.get(species_prefix, gene_name)
    assert gene is not None
    eq_(gene.name, gene_name)
    eq_(gene.mhc_class, "I")


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,fields",
    NHP_NOVEL_GENE_EXAMPLES,
)
def test_parse_nhp_novel_gene_alleles(allele_name, species_prefix, gene_name, fields):
    allele = parse(allele_name)
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, species_prefix)
    eq_(allele.gene.name, gene_name)
    eq_(allele.allele_fields, fields)
    assert allele.is_class1


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,fields",
    NHP_PSEUDOGENE_ALLELES,
)
def test_parse_nhp_pseudogene_alleles(allele_name, species_prefix, gene_name, fields):
    allele = parse(allele_name)
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, species_prefix)
    eq_(allele.gene.name, gene_name)
    eq_(allele.allele_fields, fields)
    assert allele.annotation_pseudogene
    assert allele.to_string().endswith("Ps")
