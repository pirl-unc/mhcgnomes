from mhcgnomes import parse, Gene
from nose.tools import eq_

def test_mamu_cd1b():
    seq = "rhesus macaque CD1b"
    result = parse(seq)
    eq_(result, Gene.get("Mamu", "CD1b"))

def test_mamu_cd1b_dash():
    seq = "rhesus monkey-CD1b"
    result = parse(seq)
    eq_(result, Gene.get("Mamu", "CD1b"))
