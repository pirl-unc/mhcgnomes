from mhcgnomes import NormalizingDictionary
from nose.tools import eq_

def test_test_NormalizingDictionary_from_dict_to_dict_identity():
    d = {"aA--": 1, "bb": 2}
    eq_(d, NormalizingDictionary.from_dict(d).to_dict())

def test_NormalizingDictionary_case_invariant():
    d = NormalizingDictionary.from_dict({"aA--": 1, "bb": 2})
    eq_(d["AA--"], 1)
    eq_(d["BB"], 2)

def test_NormalizingDictionary_dash_invariant():
    d = NormalizingDictionary.from_dict({"aA--": 1, "bb": 2})
    eq_(d["AA"], 1)
    eq_(d["BB-"], 2)
