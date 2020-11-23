from collections import defaultdict
from mhcgnomes.normalizing_set import NormalizingSet
from nose.tools import eq_

def test_NormalizingSet_get_original():
    s = NormalizingSet()
    item = "AB:cd"
    s.add(item)
    original = s.get_original("abcd")
    eq_(original, item)

def test_NormalizingSet_eq():
    a = NormalizingSet()
    a.add("yo")
    b = NormalizingSet()
    b.add("YO ")
    eq_(a, b)

def test_NormalizingSet_in_defaultdict():
    d = defaultdict(NormalizingSet)
    d[1].add("YO ")
    expected = NormalizingSet()
    expected.add("yo")
    eq_(d[1], expected)
