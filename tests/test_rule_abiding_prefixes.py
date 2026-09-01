"""
Three prefixes that followed no rule this library implements.

`species.yaml` mints a display prefix by one of two mechanical forms -- the
Klein two-plus-two code, or the four-plus-four the alias generator emits -- or
carries a designation with a source. These three were none of those:

    EudyChrys   four-plus-five, a shape no tier has produced since 3.42.0
                removed 5+5, while its own siblings are EudyFilh and EudyScla
    MesoCriAu   not 2+2 (Meau), not 4+4 (MesoAura), not the binomial, while the
                hamster beside it is CricGris
    NeosScha    not even a truncation of the genus: Neomonachus gives "Neom"

None was attested anywhere. They now use the 4+4 form the emitter produces, and
each keeps its old spelling as an alias so nothing already written breaks.

https://github.com/pirl-unc/mhcgnomes/issues/129
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_, ok_

# (latin name, new prefix, old prefix, a gene the species declares)
RESPELLED = [
    ("Eudyptes chrysocome", "EudyChry", "EudyChrys", "DMA"),
    ("Mesocricetus auratus", "MesoAura", "MesoCriAu", "DRA"),
    ("Neomonachus schauinslandi", "NeomScha", "NeosScha", "DRB1"),
]


@pytest.mark.parametrize("latin_name,new_prefix,old_prefix,gene_name", RESPELLED)
def test_the_new_prefix_is_the_one_the_emitter_would_make(
    latin_name, new_prefix, old_prefix, gene_name
):
    from mhcgnomes.species import _auto_generated_prefixes_for_latin_name

    species = Species.get_by_latin_name(latin_name)
    eq_(species.prefix, new_prefix)
    ok_(
        new_prefix in _auto_generated_prefixes_for_latin_name(latin_name),
        f"{new_prefix} is not a form the generator produces for {latin_name}",
    )
    ok_(
        old_prefix not in _auto_generated_prefixes_for_latin_name(latin_name),
        f"{old_prefix} turns out to be generatable after all; revisit the rename",
    )


@pytest.mark.parametrize("latin_name,new_prefix,old_prefix,gene_name", RESPELLED)
def test_provenance_is_now_generated_rather_than_unknown(
    latin_name, new_prefix, old_prefix, gene_name
):
    # The point of the change for #131: a prefix the emitter would produce is
    # one we minted, and can say so, instead of reporting None and looking like
    # an unchecked claim about the outside world.
    eq_(Species.get_by_latin_name(latin_name).prefix_provenance, "generated")


@pytest.mark.parametrize("latin_name,new_prefix,old_prefix,gene_name", RESPELLED)
def test_the_old_spelling_still_parses_and_normalizes(
    latin_name, new_prefix, old_prefix, gene_name
):
    eq_(parse(f"{old_prefix}-{gene_name}").to_string(), f"{new_prefix}-{gene_name}")
    eq_(parse(f"{new_prefix}-{gene_name}").to_string(), f"{new_prefix}-{gene_name}")
    eq_(Species.get(old_prefix).name, latin_name)


@pytest.mark.parametrize("latin_name,new_prefix,old_prefix,gene_name", RESPELLED)
def test_the_old_spelling_is_recorded_as_an_alias(latin_name, new_prefix, old_prefix, gene_name):
    species = Species.get_by_latin_name(latin_name)
    ok_(
        old_prefix in set(species.all_identifiers),
        f"{old_prefix} is no longer an identifier for {latin_name}",
    )


def test_the_siblings_that_set_the_pattern_are_unchanged():
    for prefix, latin_name in [
        ("EudyFilh", "Eudyptes filholi"),
        ("EudyScla", "Eudyptes sclateri"),
        ("CricGris", "Cricetulus griseus"),
    ]:
        eq_(Species.get_by_latin_name(latin_name).prefix, prefix)


def test_the_macaroni_penguin_collision_is_still_only_hypothetical():
    """
    EudyChry is also what the 4+4 rule gives Eudyptes chrysolophus. That species
    is not in the ontology, which is why the rename is safe today. If it is
    added, this fails and the uniqueness guard has to break the tie.
    """
    from mhcgnomes.species import latin_name_to_species_object

    ok_(
        "Eudyptes chrysolophus" not in latin_name_to_species_object,
        "the macaroni penguin was added; EudyChry now has two claimants",
    )
    eq_(Species.get("EudyChry").name, "Eudyptes chrysocome")
