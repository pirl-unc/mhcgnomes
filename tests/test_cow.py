import pytest

from mhcgnomes import Allele, Gene, parse

from .common import eq_


def test_parse_BoLA_N_04801_with_colon_gene_sep():
    # testing NetMHCpan format for BLA-N*048:01 from
    # https://www.ebi.ac.uk/ipd/mhc/allele/?accession=BoLA03255
    allele = parse("BoLA-N:04801")
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("048", "01"))


def test_parse_BoLA_N_04801():
    # testing compact format for BLA-N*048:01 from
    # https://www.ebi.ac.uk/ipd/mhc/allele/?accession=BoLA03255
    allele = parse("BoLA-N04801")
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("048", "01"))


def test_parse_BoLA_N_001001_with_colon_sep():
    allele = parse("BoLA-N:00101")
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("001", "01"))


def test_bola_nc_does_not_parse_as_n_with_letter_suffix():
    assert parse("BoLA-NC", raise_on_error=False) is None


def test_bola_nc_allele_does_not_parse_as_partial_n_allele():
    assert parse("BoLA-NC*001:01", raise_on_error=False) is None


NOVEL_CATTLE_GENE_EXAMPLES = [
    ("BoLA-DRB4*001:01", "BoLA", "DRB4", "IIa", ("001", "01")),
    ("BoLA-DRB5*001:01", "BoLA", "DRB5", "IIa", ("001", "01")),
    ("BoLA-MIC1*001:01", "BoLA", "MIC1", "Ic", ("001", "01")),
    ("BoLA-MIC2*001:01", "BoLA", "MIC2", "Ic", ("001", "01")),
    ("BoLA-MIC3*001:01", "BoLA", "MIC3", "Ic", ("001", "01")),
    ("BoLA-NC11*001:01", "BoLA", "NC11", "Ib", ("001", "01")),
    ("BoLA-NC12*001:01", "BoLA", "NC12", "Ib", ("001", "01")),
    ("BoLA-NC13*001:01", "BoLA", "NC13", "Ib", ("001", "01")),
    ("Bogr-NC12*001:01", "Bogr", "NC12", "Ib", ("001", "01")),
]


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,mhc_class,_fields",
    NOVEL_CATTLE_GENE_EXAMPLES,
)
def test_cattle_novel_gene_lookup(allele_name, species_prefix, gene_name, mhc_class, _fields):
    gene = Gene.get(species_prefix, gene_name)
    assert gene is not None
    eq_(gene.name, gene_name)
    eq_(gene.mhc_class, mhc_class)


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,mhc_class,fields",
    NOVEL_CATTLE_GENE_EXAMPLES,
)
def test_parse_cattle_novel_gene_alleles(allele_name, species_prefix, gene_name, mhc_class, fields):
    allele = parse(allele_name)
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, species_prefix)
    eq_(allele.gene.name, gene_name)
    eq_(allele.allele_fields, fields)

    if mhc_class == "IIa":
        assert allele.is_class2_beta
    else:
        assert allele.is_class1
