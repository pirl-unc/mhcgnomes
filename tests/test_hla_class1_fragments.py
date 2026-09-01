"""
The HLA class I gene fragments, and the two properties they needed.

IMGT/HLA names nine class I loci we did not carry -- N, R, S, T, U, W, X, Y and
Z -- and the reason they stayed out was never that they are unattested. It was
that adding them naively does two wrong things: it flips bare "N", "R", "S",
"U" and "Z" from mouse and rat haplotype shorthand into human gene fragments,
and it lets loci with no deposited sequence accept allele fields.

So the entries carry `context only: true` (stay out of species-less lookup) and,
where IPD-IMGT/HLA deposits nothing at all, `alleles: none`.

Allele counts checked against IPD-IMGT/HLA 3.65.0 Allelelist.txt (2026-07-14),
https://raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/Allelelist.txt

https://github.com/pirl-unc/mhcgnomes/issues/113
"""

import contextlib

import pytest

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_, ok_


@contextlib.contextmanager
def temporary_species_entry(latin_name, entry):
    """
    Add an entry to the loaded ontology for the body of a test and take it out
    again, so a failing assertion cannot leave a synthetic species behind.
    """
    from mhcgnomes.species import raw_species_dict

    raw_species_dict[latin_name] = entry
    try:
        yield
    finally:
        del raw_species_dict[latin_name]


# Every class I locus IMGT/HLA calls a "gene fragment" in its Description
# column: https://hla.alleles.org/genes/index.html
FRAGMENTS = ["N", "P", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

# The nine added for #113; P and V were already here.
CONTEXT_ONLY = ["N", "R", "S", "T", "U", "W", "X", "Y", "Z"]

# Loci IMGT/HLA names and IPD-IMGT/HLA gives zero alleles.
NO_ALLELES = ["X", "Z", "DQB3", "DPA3", "MICC", "MICD", "MICE", "PSMB8", "PSMB9"]

# One real allele name per fragment that has them, from Allelelist.txt.
ATTESTED_ALLELES = {
    "N": "N*01:01:01:01",
    "P": "P*01:01:01:01",
    "R": "R*01:01:01:01",
    "S": "S*01:01:01:01",
    "T": "T*01:01:01:01",
    "U": "U*01:01:01:01",
    "V": "V*01:01:01:01",
    "W": "W*01:01:01:01",
    "Y": "Y*01:01",
}


@pytest.mark.parametrize("gene_name", FRAGMENTS)
def test_fragment_resolves_under_the_hla_prefix(gene_name):
    gene = parse(f"HLA-{gene_name}", required_result_types=[Gene])
    eq_(gene.name, gene_name)
    ok_(gene.species.is_human)


@pytest.mark.parametrize("gene_name", FRAGMENTS)
def test_every_fragment_is_a_pseudogene(gene_name):
    ok_(Species.get("HLA").get_pseudogene_status_of_gene(gene_name))


@pytest.mark.parametrize("gene_name,allele_name", sorted(ATTESTED_ALLELES.items()))
def test_attested_allele_names_parse(gene_name, allele_name):
    allele = parse(f"HLA-{allele_name}", required_result_types=[Allele])
    eq_(allele.gene.name, gene_name)


@pytest.mark.parametrize("gene_name", NO_ALLELES)
def test_locus_without_deposited_alleles_names_no_allele(gene_name):
    # The gene itself is a real name and still resolves...
    gene = parse(f"HLA-{gene_name}", required_result_types=[Gene])
    eq_(gene.name, gene_name)
    # ...but nothing may be built on top of it. Issue #108: a confidently
    # structured answer for an input that justifies nothing is worse than None.
    eq_(parse(f"HLA-{gene_name}*01:01", raise_on_error=False), None)
    eq_(parse(f"HLA-{gene_name}*01", raise_on_error=False), None)


@pytest.mark.parametrize("gene_name", NO_ALLELES)
def test_allele_factory_refuses_a_locus_with_no_alleles(gene_name):
    # Not just the parser: the object cannot be constructed either, or callers
    # would route around the check.
    eq_(Allele.get("HLA", gene_name, "01", "01"), None)


@pytest.mark.parametrize("gene_name", CONTEXT_ONLY)
def test_context_only_fragment_never_wins_a_speciesless_parse(gene_name):
    result = parse(gene_name, raise_on_error=False)
    if result is None:
        return
    ok_(
        not (isinstance(result, Gene) and result.species.is_human),
        f"bare {gene_name!r} resolved to the human fragment: {result}",
    )


def test_bare_letters_that_are_haplotype_shorthand_stay_haplotypes():
    # The regression the nine genes had to avoid. Mouse and rat rodent
    # haplotype letters are what these strings have always meant.
    for letter, expected in [
        ("N", "RT1-n"),
        ("R", "H2-r"),
        ("S", "H2-s"),
        ("U", "H2-u"),
        ("Z", "H2-z"),
    ]:
        eq_(parse(letter).to_string(), expected)


def test_bare_letters_with_no_other_claimant_stay_unparsed():
    for letter in ["T", "W", "X", "Y"]:
        eq_(parse(letter, raise_on_error=False), None)


@pytest.mark.parametrize("gene_name", CONTEXT_ONLY)
def test_naming_the_species_resolves_a_context_only_fragment(gene_name):
    # species= is the strict form, so there is nothing left to guess.
    gene = parse(gene_name, species="Homo sapiens", required_result_types=[Gene])
    eq_(gene.name, gene_name)


@pytest.mark.parametrize("gene_name,allele_name", sorted(ATTESTED_ALLELES.items()))
def test_allele_of_a_context_only_fragment_needs_the_species_too(gene_name, allele_name):
    # "N*01:01" is standard allele format, which resolves the species from the
    # default rather than from the string, so it needs the same guard as the
    # bare gene name -- and P and V, which are not context only, keep working.
    parsed = parse(allele_name, raise_on_error=False)
    if gene_name in CONTEXT_ONLY:
        eq_(parsed, None)
    else:
        eq_(parsed.gene.name, gene_name)
    eq_(parse(f"HLA-{allele_name}", required_result_types=[Allele]).gene.name, gene_name)
    eq_(
        parse(allele_name, species="Homo sapiens", required_result_types=[Allele]).gene.name,
        gene_name,
    )


def test_naming_the_species_also_resolves_alleles_of_a_fragment():
    allele = parse("W*01:01:01:01", species="Homo sapiens", required_result_types=[Allele])
    eq_(allele.gene.name, "W")
    eq_(allele.to_string(), "HLA-W*01:01:01:01")


def test_naming_a_different_species_does_not_resolve_the_fragment():
    # The rescue is not a licence to ignore species=.
    eq_(parse("W", species="Mus musculus", raise_on_error=False), None)
    eq_(parse("N", species="Rattus norvegicus").to_string(), "Rano-n")


@pytest.mark.parametrize("gene_name", CONTEXT_ONLY)
def test_context_only_genes_are_hidden_from_species_inference(gene_name):
    human = Species.get("HLA")
    ok_(human not in Species.get_species_with_gene_name(gene_name))
    ok_(human in Species.get_species_with_gene_name(gene_name, include_context_only=True))


def test_properties_answer_for_the_genes_that_carry_them():
    human = Species.get("HLA")
    for gene_name in CONTEXT_ONLY:
        ok_(human.gene_is_context_only(gene_name))
    for gene_name in NO_ALLELES:
        ok_(human.gene_has_no_alleles(gene_name))
    # A gene absent from IPD-IMGT/HLA is not thereby allele-less: CD1 and MR1
    # vary, IMGT/HLA just does not curate them. The flag means the authority
    # names the locus and publishes nothing under it.
    for gene_name in ["A", "DRB1", "CD1a", "MR1", "N", "W"]:
        ok_(not human.gene_has_no_alleles(gene_name))
    for gene_name in ["A", "DRB1", "P", "V", "H"]:
        ok_(not human.gene_is_context_only(gene_name))


# ---------------------------------------------------------------------------
# The two new `gene properties` keys validate their values
#
# A property the loader silently ignores is worse than no property, because
# species.yaml then asserts something the runtime never reads -- the same trap
# `prefix_source` vs `prefix source` set in test_species_identity.py.
# ---------------------------------------------------------------------------

BAD_PROPERTIES = [
    # key,             value,        expected message fragment
    ("allele", "none", "Unknown properties"),  # near-miss spelling
    ("context_only", True, "Unknown properties"),  # underscore, not a space
    ("alleles", "None", "alleles"),  # capitalized: not the accepted literal
    ("alleles", "some", "alleles"),
    ("alleles", True, "alleles"),
    ("alleles", ["none"], "alleles"),
    ("context only", "true", "context only"),  # string, not a boolean
    ("context only", 1, "context only"),
]


@pytest.mark.parametrize("key,value,message", BAD_PROPERTIES)
def test_malformed_gene_properties_are_rejected(key, value, message):
    from mhcgnomes.species import create_species_for_latin_name

    entry = {
        "prefix": "TestProp",
        "name": "test",
        "genes": {"I": ["Q"]},
        "gene properties": {"Q": {key: value}},
    }
    with (
        temporary_species_entry("Test property sp.", entry),
        pytest.raises(ValueError, match=message),
    ):
        create_species_for_latin_name("Test property sp.")


@pytest.mark.parametrize(
    "latin_name,key,value",
    [
        ("Test alleles sp.", "alleles", "none"),
        ("Test context sp.", "context only", True),
    ],
)
def test_well_formed_gene_properties_load(latin_name, key, value):
    # A distinct latin name per case: create_species_for_latin_name memoizes,
    # so reusing one name would hand the second case the first one's species.
    from mhcgnomes.species import create_species_for_latin_name

    entry = {
        "prefix": "TestProp",
        "name": "test",
        "genes": {"I": ["Q"]},
        "gene properties": {"Q": {key: value}},
    }
    with temporary_species_entry(latin_name, entry):
        species = create_species_for_latin_name(latin_name)
        eq_(species.get_gene_properties("Q").get(key), value)
