"""
The runtime ontology against the designations IPD-MHC publishes.

mhcgnomes generates a prefix for any species without a curated one, guarded
only by uniqueness within this repo, so it has no knowledge of the IPD-MHC
namespace. That is how `Caau` and `Hyam` were found pointing at a goldfish and
a minnow -- by a manual sweep, months after the fact.

`mhcgnomes/data/ipd_designations.yaml` is that namespace -- all eleven groups,
125 species, transcribed verbatim from the group species tables. These tests
turn the sweep into something CI does.

https://github.com/pirl-unc/mhcgnomes/issues/112
"""

from pathlib import Path

import pytest
import yaml

from mhcgnomes import Species

from .common import eq_, ok_

DESIGNATIONS_PATH = Path(__file__).parent.parent / "mhcgnomes" / "data" / "ipd_designations.yaml"
GROUPS = yaml.safe_load(DESIGNATIONS_PATH.read_text())

ROWS = [
    (group, latin_name, code)
    for group, block in sorted(GROUPS.items())
    for latin_name, code in sorted(block["species"].items())
]

# The two rows where our prefix deliberately differs from IPD's designation,
# because another species holds the code in published use. Both are #112's
# resolution: the attested holder keeps the prefix, and the species IPD
# designates carries the code under "context only prefixes" so an explicit
# species= still reaches it.
DELIBERATE_DISAGREEMENTS = {
    ("Canis aureus", "Caau"): "Carassius auratus",
    ("Hyperoodon ampullatus", "Hyam"): "Hybognathus amarus",
}


def test_the_file_covers_the_groups_it_claims():
    # All eleven IPD-MHC groups, so the whole published namespace is checked
    # against ours in CI rather than the two thirds of it that were here first.
    eq_(
        sorted(GROUPS),
        [
            "BoLA",
            "CHICKEN",
            "CLA",
            "CeLA",
            "DLA",
            "ELA",
            "FISH",
            "NHP",
            "OLA",
            "RT1",
            "SLA",
        ],
    )
    eq_(len(ROWS), 125)


@pytest.mark.parametrize("group,latin_name,code", ROWS)
def test_every_ipd_species_is_in_our_ontology(group, latin_name, code):
    assert Species.get_by_latin_name(latin_name) is not None, (
        f"IPD-MHC lists {latin_name} in the {group} group and we do not have it"
    )


@pytest.mark.parametrize("group,latin_name,code", ROWS)
def test_our_prefix_agrees_with_ipd_or_says_why_not(group, latin_name, code):
    """
    Two outcomes are allowed. Anything else is a disagreement nobody looked at,
    which is exactly the state Caau and Hyam were in before #112.
    """
    species = Species.get_by_latin_name(latin_name)
    if species.prefix.lower() == code.lower():
        return

    expected_holder = DELIBERATE_DISAGREEMENTS.get((latin_name, code))
    assert expected_holder is not None, (
        f"{latin_name} has prefix {species.prefix!r} but IPD-MHC designates {code!r} "
        f"({GROUPS[group]['url']}). Either use the designation, or record why not."
    )
    ok_(
        code in species.context_only_mhc_prefixes,
        f"{latin_name} does not use IPD's {code!r} and does not carry it as a "
        f"context-only prefix either",
    )
    holder = Species.get(code)
    assert holder is not None, f"{code!r} resolves to nothing"
    eq_(holder.name, expected_holder)


@pytest.mark.parametrize("group,latin_name,code", ROWS)
def test_an_ipd_code_never_resolves_to_an_unrelated_species(group, latin_name, code):
    """
    The failure this issue is named for. A code IPD assigns must reach either
    the species it designates or a documented other holder -- never a third
    species that merely derived the same four letters.
    """
    holder = Species.get(code)
    # Not `if holder is None: return`. A code that resolves to nothing is the
    # other half of the same failure: two entries claiming it makes Species.get
    # ambiguous, so the designation silently stops working. All 55 resolve
    # today, and an early return here let that mutation pass.
    assert holder is not None, (
        f"IPD designates {code!r} to {latin_name}, and it now resolves to nothing -- "
        f"claimed by {[s.name for s in Species.get_multiple(code)]}"
    )
    allowed = {latin_name} | set(DELIBERATE_DISAGREEMENTS.values())
    ok_(
        holder.name in allowed,
        f"IPD designates {code!r} to {latin_name}, but it resolves to {holder.name}",
    )


def test_the_documented_disagreements_are_still_the_only_ones():
    """A canary, so a third case cannot be added to the allowlist silently."""
    actual = set()
    for _group, latin_name, code in ROWS:
        species = Species.get_by_latin_name(latin_name)
        if species is not None and species.prefix.lower() != code.lower():
            actual.add((latin_name, code))
    eq_(sorted(actual), sorted(DELIBERATE_DISAGREEMENTS))


# ---------------------------------------------------------------------------
# What the completed sweep established
# https://github.com/pirl-unc/mhcgnomes/issues/131
# ---------------------------------------------------------------------------

# Every group table read in full, and every row agreed with our prefix. Pinned
# so a later curation change that breaks the agreement has to come here.
GROUP_SIZES = {
    "BoLA": 4,
    "CHICKEN": 1,
    "CLA": 1,
    "CeLA": 33,
    "DLA": 10,
    "ELA": 1,
    "FISH": 2,
    "NHP": 66,
    "OLA": 2,
    "RT1": 2,
    "SLA": 3,
}


@pytest.mark.parametrize("group,size", sorted(GROUP_SIZES.items()))
def test_each_group_has_the_number_of_species_the_page_listed(group, size):
    eq_(len(GROUPS[group]["species"]), size)


def test_the_fish_and_chicken_groups_are_smaller_than_they_look():
    """
    A guard against a plausible-looking bulk import. IPD-MHC's FISH group is
    two species and CHICKEN is one -- not the hundreds of fish and dozens of
    birds this ontology carries. Everything else in those clades has a prefix
    we generated or a literature citation, never an IPD designation.
    """
    eq_(sorted(GROUPS["FISH"]["species"]), ["Oncorhynchus mykiss", "Salmo salar"])
    eq_(sorted(GROUPS["CHICKEN"]["species"]), ["Gallus gallus"])


def test_cattle_are_designated_at_the_genus_node_not_the_species():
    """
    IPD files cattle as "Bos sp. (BoLA)" and has no row for Bos taurus or Bos
    indicus, so their two-plus-two codes are not designations. Bota is marked
    designated from the literature instead (PMID 1559718); Boin is not marked
    at all, because nothing was found for it.
    """
    species = GROUPS["BoLA"]["species"]
    eq_(species["Bos sp."], "BoLA")
    ok_("Bos taurus" not in species, "IPD now lists Bos taurus; mark it from the page")
    ok_("Bos indicus" not in species, "IPD now lists Bos indicus; mark it from the page")
    eq_(Species.get_by_latin_name("Bos taurus").prefix_provenance, "designated")
    eq_(Species.get_by_latin_name("Bos indicus").prefix_provenance, None)
