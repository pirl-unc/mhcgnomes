"""Exact legacy BF2 spellings backed by AF013493/AF013494 (#199)."""

import json
import subprocess
import sys

import pytest

from mhcgnomes import Species, dataframe_from_string_list, parse


@pytest.mark.parametrize(
    "old, normalized, current",
    [
        ("1301", "13:01", "004:01:01"),
        ("13:01", "13:01", "004:01:01"),
        ("2101", "21:01", "021:01:01"),
        ("21:01", "21:01", "021:01:01"),
    ],
)
@pytest.mark.parametrize("prefix", ["", "Gaga-"])
@pytest.mark.parametrize("species", [None, "Gallus gallus"])
@pytest.mark.parametrize("aliases", [False, True])
def test_old_compact_and_colon_names_resolve_only_when_requested(
    old, normalized, current, prefix, species, aliases
):
    raw = f"{prefix}BF2*{old}"
    result = parse(raw, species=species, use_allele_aliases=aliases)
    assert result.to_string() == f"Gaga-BF2*{current if aliases else normalized}"
    assert result.raw_string == raw
    assert result.species == Species.get("Gallus gallus")


@pytest.mark.parametrize("name", ["004:01", "021:01", "004:01:01", "021:01:01"])
@pytest.mark.parametrize("aliases", [False, True])
def test_modern_partial_and_complete_names_keep_their_written_resolution(name, aliases):
    raw = f"Gaga-BF2*{name}"
    assert parse(raw, use_allele_aliases=aliases).to_string() == raw


@pytest.mark.parametrize("raw", ["Gaga-BF2*013:01", "Gaga-BF2*21:02", "Gaga-BF1*13:01"])
def test_the_two_exact_aliases_do_not_generalize_to_other_names(raw):
    assert parse(raw, use_allele_aliases=True).to_string() == raw


def test_public_species_alias_lookup_uses_the_same_exact_targets():
    chicken = Species.get("Gaga")
    for old, target in [("13:01", "004:01:01"), ("21:01", "021:01:01")]:
        assert chicken.get_allele_alias("BF2", old) == ("BF2", target)


@pytest.mark.parametrize("aliases", [False, True])
def test_dataframe_and_cli_follow_the_opt_in_policy(aliases):
    names = ["Gaga-BF2*1301", "Gaga-BF2*13:01", "Gaga-BF2*2101", "Gaga-BF2*21:01"]
    expected_fields = (
        ["004:01:01", "004:01:01", "021:01:01", "021:01:01"]
        if aliases
        else ["13:01", "13:01", "21:01", "21:01"]
    )
    expected = [f"Gaga-BF2*{fields}" for fields in expected_fields]
    frame = dataframe_from_string_list(names, use_allele_aliases=aliases)
    assert frame["normalized"].tolist() == expected
    assert frame["input"].tolist() == names
    flags = ["--use-allele-aliases"] if aliases else []
    rows = json.loads(
        subprocess.run(
            [sys.executable, "-m", "mhcgnomes", "--format", "json", *flags, *names],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )
    assert [row["normalized"] for row in rows] == expected
    assert [row["input"] for row in rows] == names
