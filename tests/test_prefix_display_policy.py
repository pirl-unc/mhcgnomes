"""
Printing a short prefix only where a source attests it.

Issue #129: `HLA-A*02:01` and `CyanCaer-DAB1` occupy the same canonical-output
role, though only the first is established nomenclature and the second was
minted here for runtime uniqueness. A caller cannot tell them apart from the
string. The issue proposes shipping the fix "as an explicit formatting policy
first, then become the default in a documented minor release" -- this is the
first half, so the default is unchanged and ATTESTED opts in.

The policy asks `Species.prefix_provenance`, which #131 populated: "designated"
means a URL or PMID sits beside the entry in species.yaml. So it reads a
curated judgement rather than making a new one.

https://github.com/pirl-unc/mhcgnomes/issues/129
"""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.prefix_display_policy import (
    ATTESTED,
    CURATED,
    display_prefix_for,
    get_prefix_display_policy,
    prefix_display_policy,
    set_prefix_display_policy,
)

from .common import eq_, ok_

# (input, default output, output under ATTESTED)
CASES = [
    # generated prefixes expand to the binomial nobody can mistake for a
    # published code
    ("CyanCaer-DAB1", "CyanCaer-DAB1", "CyanistesCaeruleus-DAB1"),
    ("EudyChry-DMA", "EudyChry-DMA", "EudyptesChrysocome-DMA"),
    # designated ones are left alone, which is the whole point
    ("HLA-A*02:01", "HLA-A*02:01", "HLA-A*02:01"),
    ("Mamu-A*01:01", "Mamu-A*01:01", "Mamu-A*01:01"),
    ("BoLA-DRB3*01:01", "BoLA-DRB3*01:01", "BoLA-DRB3*01:01"),
    ("Tycu-BLB*28", "Tycu-BLB*28", "Tycu-BLB*28"),
    ("H2-Kb", "H2-K*b", "H2-K*b"),
    # #129 point 6: group and non-binomial nodes keep their labels
    ("Hp-17.0", "SLA-Hp-17.0", "SLA-Hp-17.0"),
    ("HLA", "HLA", "HLA"),
]


@pytest.mark.parametrize("text,default_output,attested_output", CASES)
def test_the_default_is_unchanged(text, default_output, attested_output):
    eq_(parse(text).to_string(), default_output)


@pytest.mark.parametrize("text,default_output,attested_output", CASES)
def test_attested_expands_only_the_prefixes_we_minted(text, default_output, attested_output):
    with prefix_display_policy(ATTESTED):
        eq_(parse(text).to_string(), attested_output)


@pytest.mark.parametrize("text,default_output,attested_output", CASES)
def test_both_spellings_parse_under_either_policy(text, default_output, attested_output):
    """
    #129's compatibility requirement: "the intentional compatibility change is
    normalized/display output rather than loss of accepted inputs."
    """
    for policy in (CURATED, ATTESTED):
        with prefix_display_policy(policy):
            for spelling in (default_output, attested_output):
                ok_(
                    parse(spelling, raise_on_error=False) is not None, f"{spelling} stopped parsing"
                )


def test_the_expanded_form_round_trips():
    with prefix_display_policy(ATTESTED):
        expanded = parse("CyanCaer-DAB1").to_string()
        eq_(expanded, "CyanistesCaeruleus-DAB1")
        eq_(parse(expanded).to_string(), expanded)


# ---------------------------------------------------------------------------
# The policy itself
# ---------------------------------------------------------------------------


def test_the_policy_restores_itself_even_when_the_block_raises():
    eq_(get_prefix_display_policy(), CURATED)
    with pytest.raises(RuntimeError), prefix_display_policy(ATTESTED):
        raise RuntimeError("boom")
    eq_(get_prefix_display_policy(), CURATED)


def test_nesting_restores_the_outer_policy():
    with prefix_display_policy(ATTESTED):
        with prefix_display_policy(CURATED):
            eq_(parse("CyanCaer-DAB1").to_string(), "CyanCaer-DAB1")
        eq_(parse("CyanCaer-DAB1").to_string(), "CyanistesCaeruleus-DAB1")
    eq_(get_prefix_display_policy(), CURATED)


def test_an_unknown_policy_is_refused():
    with pytest.raises(ValueError, match="Unknown prefix display policy"):
        set_prefix_display_policy("binomial-always")
    eq_(get_prefix_display_policy(), CURATED)


def test_another_thread_is_unaffected():
    """
    Thread-local, so a policy set for one caller cannot change what another is
    midway through formatting.
    """
    import threading

    seen = []

    def read_in_thread():
        seen.append(parse("CyanCaer-DAB1").to_string())

    with prefix_display_policy(ATTESTED):
        eq_(parse("CyanCaer-DAB1").to_string(), "CyanistesCaeruleus-DAB1")
        thread = threading.Thread(target=read_in_thread)
        thread.start()
        thread.join()

    eq_(seen, ["CyanCaer-DAB1"])


def test_the_policy_reads_provenance_rather_than_guessing():
    human = Species.get_by_latin_name("Homo sapiens")
    tit = Species.get_by_latin_name("Cyanistes caeruleus")
    eq_(human.prefix_provenance, "designated")
    ok_(tit.prefix_provenance != "designated")
    with prefix_display_policy(ATTESTED):
        eq_(display_prefix_for(human), "HLA")
        eq_(display_prefix_for(tit), "CyanistesCaeruleus")


def test_a_trinomial_keeps_its_curated_prefix():
    """
    The emitter declines trinomials, so there is no binomial to expand to and
    the curated label stands under either policy.
    """
    owl = Species.get_by_latin_name("Strix occidentalis caurina")
    with prefix_display_policy(ATTESTED):
        eq_(display_prefix_for(owl), owl.canonical_mhc_prefix)
