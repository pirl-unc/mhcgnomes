"""
Gene names from MHC-region downloads that do not name an MHC molecule.

The dangerous case is a name the parser can split into a real locus plus an
allele-like suffix: "Kdm5d" under a mouse species became `H2-K*dm5d` and
"Daxx" became `H2-D*axx`. Both look syntactically valid and are dispatched
onward, so the false positive is silent.

https://github.com/pirl-unc/mhcgnomes/issues/133
"""

import pytest

from mhcgnomes import Species, parse, parse_gene_class
from mhcgnomes.non_mhc_genes import NON_MHC_REGION_GENE_NAMES, is_non_mhc_gene_name

from .common import eq_, ok_

# The five reported in #133, all HGNC-approved symbols for non-MHC proteins.
REPORTED = ["Kdm5d", "Daxx", "Col11a2", "Atp6v1g2", "Arhgap45"]

# The two that were split into a mouse locus plus an allele suffix, with what
# they wrongly produced.
SPLIT_INTO_MOUSE_LOCUS = [("Kdm5d", "H2-K*dm5d"), ("Daxx", "H2-D*axx")]


@pytest.mark.parametrize("gene_name", REPORTED)
def test_non_mhc_gene_does_not_parse_as_an_allele(gene_name):
    eq_(parse(gene_name, species="Mus musculus", raise_on_error=False), None)


@pytest.mark.parametrize("gene_name,was", SPLIT_INTO_MOUSE_LOCUS)
def test_the_locus_plus_suffix_split_is_refused(gene_name, was):
    """Named separately from the test above because this is the silent one."""
    result = parse(gene_name, species="Mus musculus", raise_on_error=False)
    assert result is None, f"{gene_name!r} still parses as {result.to_string()} (was {was})"


@pytest.mark.parametrize("gene_name", REPORTED)
def test_non_mhc_gene_is_classified_rather_than_guessed(gene_name):
    info = parse_gene_class(gene_name, species="Mus musculus", raise_on_error=False)
    assert info is not None, f"{gene_name!r} returned None instead of a non-MHC classification"
    ok_(info.non_mhc)
    eq_(info.mhc_class, "other")


@pytest.mark.parametrize("gene_name", REPORTED)
def test_reported_names_are_in_the_curated_table(gene_name):
    ok_(is_non_mhc_gene_name(gene_name))
    ok_(is_non_mhc_gene_name(gene_name.upper()))
    ok_(is_non_mhc_gene_name(gene_name.lower()))


# Most of the table is real genes in the ontology, so the parser guard has to
# key on "the species does not declare it" rather than on the name alone.
DECLARED_AND_MUST_STILL_PARSE = ["TAP1", "TAP2", "TAPBP", "B2M", "RING4", "PSF1", "TAP-L"]


@pytest.mark.parametrize("gene_name", DECLARED_AND_MUST_STILL_PARSE)
def test_a_declared_gene_in_the_table_still_parses(gene_name):
    result = parse(gene_name, species="Homo sapiens", raise_on_error=False)
    assert result is not None, f"{gene_name!r} stopped parsing"
    eq_(result.species.name, "Homo sapiens")


def test_the_guard_only_fires_for_names_no_species_declares():
    """
    The invariant behind the guard: every reported name is absent from the
    whole ontology, so refusing it cannot shadow a real locus.
    """
    from mhcgnomes.species import latin_name_to_species_object

    for gene_name in REPORTED:
        owners = [
            species.name
            for species in latin_name_to_species_object.values()
            if species.find_matching_gene_name(gene_name) is not None
        ]
        eq_(owners, [], f"{gene_name} is declared by {owners}")


@pytest.mark.parametrize(
    "name,species",
    [
        ("H2-K", None),
        ("H2-Kb", None),
        ("H2-D", None),
        ("HLA-A*02:01", None),
        # A bare locus needs a species either way -- parse("Kb") is None on
        # 3.43.2 as well, so the guard must not be blamed for it.
        ("Kb", "Mus musculus"),
        ("K", "Mus musculus"),
    ],
)
def test_real_mouse_and_human_names_are_unaffected(name, species):
    result = (
        parse(name, species=species, raise_on_error=False)
        if species
        else parse(name, raise_on_error=False)
    )
    assert result is not None, f"{name!r} stopped parsing"


def test_table_values_name_genes_that_exist():
    """
    Each entry maps to the canonical gene it stands for. For the historic
    aliases that is a different name (RING4 -> TAP1); for the #133 additions it
    is the symbol itself, since no species declares them.
    """
    human = Species.get("HLA")
    for alias, canonical in NON_MHC_REGION_GENE_NAMES.items():
        if human.find_matching_gene_name(canonical) is not None:
            continue
        eq_(alias, canonical, f"{alias} maps to {canonical}, which no species declares")
