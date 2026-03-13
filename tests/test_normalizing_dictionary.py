import pytest

from mhcgnomes import NormalizingDictionary

from .common import eq_


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


def test_NormalizingDictionary_copy_is_independent():
    original = NormalizingDictionary.from_dict({"AA--": 1, "bb": 2})
    copied = original.copy()
    copied["cc"] = 3

    assert "cc" not in original
    eq_(copied["CC"], 3)


def test_NormalizingDictionary_original_key_ambiguity_and_pick_best():
    d = NormalizingDictionary(("AA--", 1), ("aa", 2))

    eq_(d.original_keys("A-A"), {"AA--", "aa"})
    with pytest.raises(ValueError):
        d.original_key("A-A")
    eq_(d.original_key("A-A", pick_best_fn=lambda ks: sorted(ks)[0]), "AA--")


def test_NormalizingDictionary_default_value_fn_populates_missing_key():
    d = NormalizingDictionary(default_value_fn=list)

    value = d["missing"]

    eq_(value, [])
    assert "missing" in d


def test_NormalizingDictionary_map_keys_map_values_and_invert():
    d = NormalizingDictionary(("a", 1), ("b", (1, 2)))

    mapped_values = d.map_values(
        lambda value: tuple(value) if isinstance(value, tuple) else value + 10
    )
    mapped_keys = d.map_keys(lambda key: f"{key}{key}")
    inverted = d.invert()

    eq_(mapped_values["a"], 11)
    eq_(mapped_values["b"], (1, 2))
    eq_(mapped_keys["AA"], 1)
    eq_(inverted[1], {"a", "b"})
    eq_(inverted[2], {"b"})


def test_NormalizingDictionary_key_alignment_prefers_sorted_original_keys():
    d = NormalizingDictionary(("bb", 1), ("AA--", 2), ("aa", 3))

    aligned = list(d.keys_aligned_with_values())
    key_sets = dict(d.key_sets_aligned_with_values())

    eq_(len(d), 2)
    eq_(set(aligned), {"AA--", "bb"})
    eq_(key_sets["AA"], {"AA--", "aa"})
