"""
Every allele-alias key must be reachable (#216).

Alias keys are old names, written with the digits their authors used. The
parser used to zero-pad allele fields before transform_parse_candidate looked
the name up, so a key narrower than the gene's canonical width could never
match: the curated "Mamu-B*08 -> B*008:01" saw "B*008", and "MICA*00201" was
split and padded into "MICA*000:201". 21 keys were dead that way.
"""

import pytest

from mhcgnomes import Gene, parse
from mhcgnomes.data import allele_aliases


def _gene_bearing_alias_keys():
    for prefix, table in allele_aliases.items():
        # .keys() gives every original spelling; iterating gives one per entry.
        for key in sorted(table.keys()):
            target = table[key]
            # Gene-less targets (Saha's SahaI*NN) have no "<prefix>-<target>"
            # spelling to compare against; test_saha covers them.
            if "*" in str(target):
                yield prefix, key, target


def test_every_alias_key_resolves_to_its_target():
    failures = []
    checked = 0
    for prefix, key, target in _gene_bearing_alias_keys():
        checked += 1
        got = parse(f"{prefix}-{key}", use_allele_aliases=True, raise_on_error=False)
        want = parse(f"{prefix}-{target}", use_allele_aliases=True, raise_on_error=False)
        if want is None:
            failures.append((prefix, key, f"target {target!r} does not parse"))
        elif got != want:
            failures.append((prefix, key, f"{got} != {want.to_string()}"))
        elif parse(got.to_string(), use_allele_aliases=True) != got:
            failures.append((prefix, key, "resolved name is not stable on reparse"))
    assert checked > 3000
    assert failures == []


# NetMHC 4.0's short rhesus macaque names, with the full name its
# MHC_allele_names.txt gives for each (NetMHCpan 4.1 adds Mamu-A26).
NETMHC_MAMU_SHORT_NAMES = {
    "Mamu-A01": "Mamu-A1*001:01",
    "Mamu-A02": "Mamu-A1*002:01",
    "Mamu-A07": "Mamu-A1*007:01",
    "Mamu-A11": "Mamu-A1*011:01",
    "Mamu-A26": "Mamu-A1*026:01",
    "Mamu-B01": "Mamu-B*001:01",
    "Mamu-B03": "Mamu-B*003:01",
    "Mamu-B08": "Mamu-B*008:01",
    "Mamu-B52": "Mamu-B*052:01",
}


@pytest.mark.parametrize("name, expected", sorted(NETMHC_MAMU_SHORT_NAMES.items()))
def test_netmhc_mamu_short_name_resolves_with_aliases(name, expected):
    assert parse(name, use_allele_aliases=True).to_string() == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Mamu-B*08", "Mamu-B*008:01"),
        ("Mamu-B*17", "Mamu-B*017:01"),
        ("Mamu-B*39:01", "Mamu-B*039:01"),
        ("Mamu-A1*1701", "Mamu-A1*007:04"),
        ("Mamu-A1*5801", "Mamu-A1*061:01"),
        ("Mamu-A1*030102", "Mamu-A1*003:14"),
        ("HLA-MICA*00201", "HLA-MICA*002:01:01"),
        ("HLA-MICB*00501", "HLA-MICB*005:01:01"),
    ],
)
def test_old_name_narrower_than_canonical_resolves(name, expected):
    assert parse(name, use_allele_aliases=True).to_string() == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        # Default parsing is unchanged by #216: without alias resolution the
        # fields are still zero-padded.
        ("Mamu-B08", "Mamu-B*008"),
        ("Mamu-A01", "Mamu-A*01"),
        ("HLA-MICA*00201", "HLA-MICA*000:201"),
    ],
)
def test_default_parsing_still_pads(name, expected):
    assert parse(name).to_string() == expected


def test_current_names_are_not_mistaken_for_old_ones():
    # B*008 is the current Mamu-B*008 lineage, not the old name B*08.
    assert parse("Mamu-B*008", use_allele_aliases=True).to_string() == "Mamu-B*008"
    assert parse("Mamu-B*008:01", use_allele_aliases=True).to_string() == "Mamu-B*008:01"


@pytest.mark.parametrize("use_allele_aliases", [False, True])
def test_bare_mamu_b17_is_the_ipd_locus(use_allele_aliases):
    # NetMHC's short name Mamu-B17 means B*017:01, but Mamu-B17 is also an
    # IPD-MHC locus (Mamu-B17*01:01:01 ... *01:08, e.g. NHP02096), so the bare
    # name stays the gene rather than shadowing it.
    result = parse("Mamu-B17", use_allele_aliases=use_allele_aliases)
    assert type(result) is Gene
    assert result.name == "B17"
    assert parse("Mamu-B17*01:02:02").gene_name == "B17"
