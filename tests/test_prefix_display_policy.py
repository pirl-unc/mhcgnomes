"""
Printing a short prefix only where a source attests it, with CURATED kept as an
explicit compact output mode.

Issues #129 and #188:
- Default output (ATTESTED) uses the complete scientific-name form for
  generated or unestablished prefixes (e.g. ``CyanistesCaeruleus-DAB1``,
  ``HypophthalmichthysMolitrix-DAB``), while source-designated short codes
  (``HLA``, ``Mamu``, ``BoLA``, ``SLA``, ``H2``, ``Tycu``) stay short.
- Existing 2+2 and 4+4 forms continue to parse under either policy.
- CURATED explicitly emits the ontology's compact prefix (including
  ``HypoMoli-DAB``) across all nested/species-bearing result types.

https://github.com/pirl-unc/mhcgnomes/issues/129
https://github.com/pirl-unc/mhcgnomes/issues/188
"""

import pytest

from mhcgnomes import (
    Allele,
    AmbiguousAlleles,
    Class2Locus,
    Gene,
    Haplotype,
    Pair,
    Serotype,
    Species,
    Supertype,
    parse,
)
from mhcgnomes.prefix_display_policy import (
    ATTESTED,
    CURATED,
    display_prefix_for,
    get_prefix_display_policy,
    prefix_display_policy,
    set_prefix_display_policy,
)

from .common import eq_, ok_

# (accepted input, default ATTESTED output, explicit CURATED compact output)
CASES = [
    # generated prefixes expand to the full binomial by default, while CURATED
    # emits the compact 4+4 prefix (#129, #188)
    ("CyanCaer-DAB1", "CyanistesCaeruleus-DAB1", "CyanCaer-DAB1"),
    ("HypoMoli-DAB", "HypophthalmichthysMolitrix-DAB", "HypoMoli-DAB"),
    ("EudyChry-DMA", "EudyptesChrysocome-DMA", "EudyChry-DMA"),
    # designated ones are unchanged under either policy
    ("HLA-A*02:01", "HLA-A*02:01", "HLA-A*02:01"),
    ("Mamu-A*01:01", "Mamu-A*01:01", "Mamu-A*01:01"),
    ("BoLA-DRB3*01:01", "BoLA-DRB3*01:01", "BoLA-DRB3*01:01"),
    ("Tycu-BLB*28", "Tycu-BLB*28", "Tycu-BLB*28"),
    ("H2-Kb", "H2-K*b", "H2-K*b"),
    # #129 point 6: group and non-binomial nodes keep their labels
    ("Hp-17.0", "SLA-Hp-17.0", "SLA-Hp-17.0"),
    ("HLA", "HLA", "HLA"),
]


@pytest.mark.parametrize("text,default_output,curated_output", CASES)
def test_default_attested_output(text, default_output, curated_output):
    eq_(get_prefix_display_policy(), ATTESTED)
    eq_(parse(text).to_string(), default_output)


@pytest.mark.parametrize("text,default_output,curated_output", CASES)
def test_curated_compact_output(text, default_output, curated_output):
    with prefix_display_policy(CURATED):
        eq_(parse(text).to_string(), curated_output)


@pytest.mark.parametrize("text,default_output,curated_output", CASES)
def test_both_spellings_parse_under_either_policy(text, default_output, curated_output):
    """
    #129/#188 compatibility requirement: accepted 2+2, 4+4, and full-binomial
    inputs keep parsing identically under either display policy.
    """
    for policy in (ATTESTED, CURATED):
        with prefix_display_policy(policy):
            for spelling in (text, default_output, curated_output):
                ok_(
                    parse(spelling, raise_on_error=False) is not None, f"{spelling} stopped parsing"
                )


def test_the_expanded_form_round_trips():
    expanded = parse("CyanCaer-DAB1").to_string()
    eq_(expanded, "CyanistesCaeruleus-DAB1")
    eq_(parse(expanded).to_string(), expanded)


def test_three_contracts_for_hypomoli_dab():
    """Explicitly distinguish accepted input, default output, and CURATED compact output (#188)."""
    for accepted_input, kwargs in [
        ("HypoMoli-DAB", {}),
        ("HypophthalmichthysMolitrix-DAB", {}),
        ("Hymo-DAB", {"species": "Hypophthalmichthys molitrix"}),
    ]:
        parsed = parse(accepted_input, raise_on_error=True, **kwargs)
        eq_(parsed.species.name, "Hypophthalmichthys molitrix")
        # Default output (ATTESTED): full binomial
        eq_(parsed.to_string(), "HypophthalmichthysMolitrix-DAB")
        # Requested compact output (CURATED): exact 4+4 prefix
        with prefix_display_policy(CURATED):
            eq_(parsed.to_string(), "HypoMoli-DAB")


def test_curated_and_attested_apply_to_all_nested_result_types():
    """CURATED and ATTESTED govern Species, Gene, Allele, Pair, Haplotype, AmbiguousAlleles, Serotype, Supertype, and Class2Locus (#188)."""
    sp = Species.get_by_latin_name("Hypophthalmichthys molitrix")
    dab_gene = Gene.get(sp, "DAB")
    daa_gene = Gene.get(sp, "DAA")
    a1 = Allele.get(sp, "DAB", "01", "01")
    a2 = Allele.get(sp, "DAB", "02", "01")
    alpha = Allele.get(sp, "DAA", "01", "01")
    pair = Pair.get(alpha=alpha, beta=a1)
    locus = Class2Locus.get(sp, "DA")
    hap = Haplotype(species=sp, name="h1", alleles=(alpha, a1))
    ambig = AmbiguousAlleles(species=sp, alleles=(a1, a2))
    sero = Serotype(species=sp, name="DA1", alleles=(a1,))
    sup = Supertype(species=sp, name="S1", alleles=(a1,), representative=a1)

    expected_attested = [
        (sp, "HypophthalmichthysMolitrix"),
        (dab_gene, "HypophthalmichthysMolitrix-DAB"),
        (daa_gene, "HypophthalmichthysMolitrix-DAA"),
        (a1, "HypophthalmichthysMolitrix-DAB*01:01"),
        (pair, "HypophthalmichthysMolitrix-DAA*01:01/DAB*01:01"),
        (locus, "HypophthalmichthysMolitrix-DA"),
        (hap, "HypophthalmichthysMolitrix-h1"),
        (ambig, "HypophthalmichthysMolitrix-DAB*01:01/DAB*02:01"),
        (sero, "HypophthalmichthysMolitrix-DA1"),
        (sup, "HypophthalmichthysMolitrix S1 supertype"),
    ]
    for obj, expected in expected_attested:
        eq_(obj.to_string(), expected)

    expected_curated = [
        (sp, "HypoMoli"),
        (dab_gene, "HypoMoli-DAB"),
        (daa_gene, "HypoMoli-DAA"),
        (a1, "HypoMoli-DAB*01:01"),
        (pair, "HypoMoli-DAA*01:01/DAB*01:01"),
        (locus, "HypoMoli-DA"),
        (hap, "HypoMoli-h1"),
        (ambig, "HypoMoli-DAB*01:01/DAB*02:01"),
        (sero, "HypoMoli-DA1"),
        (sup, "HypoMoli S1 supertype"),
    ]
    with prefix_display_policy(CURATED):
        for obj, expected in expected_curated:
            eq_(obj.to_string(), expected)


def test_all_mhc_prefixes_has_no_duplicates_and_keeps_curated_alias():
    sp = Species.get_by_latin_name("Cyanistes caeruleus")
    prefixes = sp.all_mhc_prefixes
    eq_(len(prefixes), len(set(prefixes)))
    eq_(prefixes[0], "CyanistesCaeruleus")
    ok_("CyanCaer" in prefixes)
    with prefix_display_policy(CURATED):
        curated_prefixes = sp.all_mhc_prefixes
        eq_(len(curated_prefixes), len(set(curated_prefixes)))
        eq_(curated_prefixes[0], "CyanCaer")
        ok_("CyanistesCaeruleus" in curated_prefixes)


# ---------------------------------------------------------------------------
# The policy itself
# ---------------------------------------------------------------------------


def test_the_policy_restores_itself_even_when_the_block_raises():
    eq_(get_prefix_display_policy(), ATTESTED)
    with pytest.raises(RuntimeError), prefix_display_policy(CURATED):
        raise RuntimeError("boom")
    eq_(get_prefix_display_policy(), ATTESTED)


def test_nesting_restores_the_outer_policy():
    with prefix_display_policy(CURATED):
        with prefix_display_policy(ATTESTED):
            eq_(parse("CyanCaer-DAB1").to_string(), "CyanistesCaeruleus-DAB1")
        eq_(parse("CyanCaer-DAB1").to_string(), "CyanCaer-DAB1")
    eq_(get_prefix_display_policy(), ATTESTED)


def test_an_unknown_policy_is_refused():
    with pytest.raises(ValueError, match="Unknown prefix display policy"):
        set_prefix_display_policy("binomial-always")
    eq_(get_prefix_display_policy(), ATTESTED)


def test_another_thread_is_unaffected():
    """
    Thread-local, so a policy set for one caller cannot change what another is
    midway through formatting.
    """
    import threading

    seen = []

    def read_in_thread():
        seen.append(parse("CyanCaer-DAB1").to_string())

    with prefix_display_policy(CURATED):
        eq_(parse("CyanCaer-DAB1").to_string(), "CyanCaer-DAB1")
        thread = threading.Thread(target=read_in_thread)
        thread.start()
        thread.join()

    eq_(seen, ["CyanistesCaeruleus-DAB1"])


def test_the_policy_reads_provenance_rather_than_guessing():
    human = Species.get_by_latin_name("Homo sapiens")
    tit = Species.get_by_latin_name("Cyanistes caeruleus")
    eq_(human.prefix_provenance, "designated")
    ok_(tit.prefix_provenance != "designated")
    eq_(display_prefix_for(human), "HLA")
    eq_(display_prefix_for(tit), "CyanistesCaeruleus")
    with prefix_display_policy(CURATED):
        eq_(display_prefix_for(human), "HLA")
        eq_(display_prefix_for(tit), "CyanCaer")


def test_a_trinomial_keeps_its_curated_prefix():
    """
    The emitter declines trinomials, so there is no binomial to expand to and
    the curated label stands under either policy.
    """
    owl = Species.get_by_latin_name("Strix occidentalis caurina")
    eq_(display_prefix_for(owl), owl.canonical_mhc_prefix)
    with prefix_display_policy(CURATED):
        eq_(display_prefix_for(owl), owl.canonical_mhc_prefix)
