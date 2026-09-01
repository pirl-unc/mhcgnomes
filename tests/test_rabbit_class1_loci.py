"""
The rabbit class I locus series, and the ambiguity adding it creates.

`Orcu-U2*05:02:01:01` is deposited in GenBank and did not parse: Oryctolagus
cuniculus declared no genes of its own, inheriting A/A1/A2/A3/D from
Oryctolagus sp. -- the older RLA-A nomenclature. GenBank carries a second,
systematic series across 104 records, Orcu-U1 through Orcu-U9, submitted
alongside Zhang et al., PNAS 2026;123:e2532064123 (PMID 42113988).

Adding it makes bare "U1" and "U2" genuinely ambiguous, because Rattus sp.
declares those two as well. Under the #130 rule they stop resolving, which is
the honest answer: nothing attests the bare form for either species, and the
rat only won them by being the sole declarer.

https://github.com/pirl-unc/mhcgnomes/issues/170
https://www.ncbi.nlm.nih.gov/nuccore/PV167019.1
"""

import pytest

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_, ok_

RABBIT_LOCI = ["U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9"]

# The two the rat also declares, as RT1-U1 and RT1-U2.
SHARED_WITH_RAT = ["U1", "U2"]


@pytest.mark.parametrize("gene_name", RABBIT_LOCI)
def test_each_rabbit_locus_resolves_under_its_prefix(gene_name):
    gene = parse(f"Orcu-{gene_name}", required_result_types=[Gene])
    eq_(gene.name, gene_name)
    eq_(gene.species.name, "Oryctolagus cuniculus")


def test_the_deposited_allele_name_parses():
    allele = parse("Orcu-U2*05:02:01:01", required_result_types=[Allele])
    eq_(allele.to_string(), "Orcu-U2*05:02:01:01")
    eq_(allele.gene.name, "U2")


@pytest.mark.parametrize("gene_name", SHARED_WITH_RAT)
def test_a_locus_both_species_declare_names_neither_on_its_own(gene_name):
    rat = Species.get_by_latin_name("Rattus sp.")
    rabbit = Species.get_by_latin_name("Oryctolagus cuniculus")
    ok_(rat.declares_gene(gene_name), f"Rattus sp. no longer declares {gene_name}")
    ok_(rabbit.declares_gene(gene_name), f"the rabbit no longer declares {gene_name}")
    # Bare resolved to the rat before this, only because the rat was the sole
    # declarer. Both prefixed forms still work, which is the point.
    eq_(parse(gene_name, raise_on_error=False), None)
    eq_(parse(f"{gene_name}*01:01", raise_on_error=False), None)
    eq_(parse(f"RT1-{gene_name}").species.name, "Rattus sp.")
    eq_(parse(f"Orcu-{gene_name}").species.name, "Oryctolagus cuniculus")


@pytest.mark.parametrize("gene_name", [g for g in RABBIT_LOCI if g not in SHARED_WITH_RAT])
def test_a_locus_only_the_rabbit_declares_still_resolves_bare(gene_name):
    eq_(parse(gene_name).species.name, "Oryctolagus cuniculus")


def test_the_older_rla_nomenclature_is_untouched():
    """
    A/A1/A2/A3/D sit on Oryctolagus sp. under the RLA prefix (PMID 32522857).
    How that series relates to Orcu-U1..U9 is the open half of #170, so nothing
    here merges or replaces them.
    """
    eq_(parse("RLA-A1*01:01").to_string(), "RLA-A1*01:01")
    eq_(parse("Orcu-A1").species.name, "Oryctolagus cuniculus")
    eq_(parse("RLA-A1").species.name, "Oryctolagus sp.")


def test_the_bare_species_code_is_not_a_gene_name():
    """
    21 older GenBank records label the gene with the species code itself and
    write alleles as "Orcu*19" (KU848263.1). Adding that would make a prefix
    its own gene name -- the shape that put a class II beta chain symbol in the
    prefix column for the greater prairie chicken (#165).
    """
    eq_(parse("Orcu*19", raise_on_error=False), None)
    ok_(not Species.get_by_latin_name("Oryctolagus cuniculus").declares_gene("Orcu"))


def test_the_loci_sit_on_the_species_not_the_genus_node():
    # The records name Oryctolagus cuniculus, so that is where they go. RLA-U2
    # is not a deposited spelling and does not resolve.
    eq_(parse("RLA-U2", raise_on_error=False), None)
    rabbit = Species.get_by_latin_name("Oryctolagus cuniculus")
    genus = Species.get_by_latin_name("Oryctolagus sp.")
    for gene_name in RABBIT_LOCI:
        ok_(rabbit.declares_gene(gene_name), f"{gene_name} left the species entry")
        ok_(not genus.declares_gene(gene_name), f"{gene_name} moved up to the genus node")
