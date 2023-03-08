from mhcgnomes import NormalizingDictionary

def test_test_NormalizingDictionary_from_dict_to_dict_identity():
    d = {"aA--": 1, "bb": 2}
    assert d == NormalizingDictionary.from_dict(d).to_dict()

def test_NormalizingDictionary_case_invariant():
    d = NormalizingDictionary.from_dict({"aA--": 1, "bb": 2})
    assert d["AA--"] == 1
    assert d["BB"] == 2

def test_NormalizingDictionary_dash_invariant():
    d = NormalizingDictionary.from_dict({"aA--": 1, "bb": 2})
    assert d["AA"] == 1
    assert d["BB-"] == 2
