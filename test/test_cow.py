from nose.tools import eq_
from mhcgnomes import parse, Allele

def test_parse_BoLA_N_04801_with_colon_gene_sep():
    # testing NetMHCpan format for BLA-N*048:01 from
    # https://www.ebi.ac.uk/ipd/mhc/allele/?accession=BoLA03255
    allele = parse('BoLA-N:04801')
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("048", "01"))

def test_parse_BoLA_N_04801():
    # testing compact format for BLA-N*048:01 from
    # https://www.ebi.ac.uk/ipd/mhc/allele/?accession=BoLA03255
    allele = parse('BoLA-N04801')
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("048", "01"))

def test_parse_BoLA_N_001001_with_colon_sep():
    allele = parse('BoLA-N:00101')
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "BoLA")
    eq_(allele.gene.name, "N")
    eq_(allele.allele_fields, ("001", "01"))
