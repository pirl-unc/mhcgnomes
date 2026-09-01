import pytest

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_

CETACEAN_SPECIES = [
    ("Bamu", "Balaenoptera musculus"),
    ("Baac", "Balaenoptera acutorostrata"),
    ("Baed", "Balaenoptera edeni"),
    ("Cehe", "Cephalorhynchus hectori"),
    ("Dede", "Delphinus delphis"),
    ("Euau", "Eubalaena australis"),
    ("Glme", "Globicephala melas"),
    ("Grgr", "Grampus griseus"),
    ("Kobr", "Kogia breviceps"),
    ("Laob", "Lagenorhynchus obscurus"),
    ("Mede", "Mesoplodon densirostris"),
    ("Meeu", "Mesoplodon europaeus"),
    ("Megr", "Mesoplodon grayi"),
    ("Meno", "Megaptera novaeangliae"),
    ("Stbr", "Steno bredanensis"),
    ("Stco", "Stenella coeruleoalba"),
    ("Tutr", "Tursiops truncatus"),
    ("Zica", "Ziphius cavirostris"),
]

CETACEAN_REPRESENTATIVE_ALLELES = [
    ("Bamu-DQA*001:01:01", "Bamu", "DQA", ("001", "01", "01")),
    ("Baac-S*001:01", "Baac", "S", ("001", "01")),
    ("Baed-DQB*001:01", "Baed", "DQB", ("001", "01")),
    ("Cehe-DRA*001:01", "Cehe", "DRA", ("001", "01")),
    ("Dede-N*001:01", "Dede", "N", ("001", "01")),
    ("Euau-DQA*001:01:01", "Euau", "DQA", ("001", "01", "01")),
    ("Glme-DQB*001:01", "Glme", "DQB", ("001", "01")),
    ("Grgr-N*001:01", "Grgr", "N", ("001", "01")),
    ("Kobr-DRA*001:01", "Kobr", "DRA", ("001", "01")),
    ("Laob-N*001:01", "Laob", "N", ("001", "01")),
    ("Mede-DQA*001:01:01", "Mede", "DQA", ("001", "01", "01")),
    ("Meeu-DQB*001:01", "Meeu", "DQB", ("001", "01")),
    ("Megr-DRA*001:01", "Megr", "DRA", ("001", "01")),
    ("Meno-DQB*001:01", "Meno", "DQB", ("001", "01")),
    ("Stbr-N*001:01", "Stbr", "N", ("001", "01")),
    ("Stco-DRA*001:01", "Stco", "DRA", ("001", "01")),
    ("Tutr-N*001:01", "Tutr", "N", ("001", "01")),
    ("Zica-DRA*001:01", "Zica", "DRA", ("001", "01")),
]

CETACEAN_GENE_EXAMPLES = [
    ("Bamu-DQA*001:01:01", "Bamu", "DQA", "IIa", ("001", "01", "01"), "alpha"),
    ("Bamu-DQB*001:01", "Bamu", "DQB", "IIa", ("001", "01"), "beta"),
    ("Bamu-DRA*001:01", "Bamu", "DRA", "IIa", ("001", "01"), "alpha"),
    ("Bamu-DRB1*001:01", "Bamu", "DRB1", "IIa", ("001", "01"), "beta"),
    ("Bamu-N*001:01", "Bamu", "N", "I", ("001", "01"), None),
    ("Baac-S*001:01", "Baac", "S", "I", ("001", "01"), None),
]


@pytest.mark.parametrize("species_prefix,species_name", CETACEAN_SPECIES)
def test_cetacean_species_registered(species_prefix, species_name):
    species = Species.get(species_prefix)
    assert species is not None
    eq_(species.name, species_name)
    eq_(species.historic_mhc_prefix, "CELA")


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,mhc_class,fields,chain_type",
    CETACEAN_GENE_EXAMPLES,
)
def test_cetacean_gene_metadata(
    allele_name, species_prefix, gene_name, mhc_class, fields, chain_type
):
    gene = Gene.get(species_prefix, gene_name)
    assert gene is not None
    eq_(gene.species.prefix, species_prefix)
    eq_(gene.name, gene_name)
    eq_(gene.mhc_class, mhc_class)

    parsed_gene = parse(f"{species_prefix}-{gene_name}")
    eq_(parsed_gene, gene)

    allele = parse(allele_name)
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, species_prefix)
    eq_(allele.gene.name, gene_name)
    eq_(allele.allele_fields, fields)

    if chain_type == "alpha":
        assert allele.is_class2_alpha
    elif chain_type == "beta":
        assert allele.is_class2_beta
    else:
        assert allele.is_class1


@pytest.mark.parametrize(
    "allele_name,species_prefix,gene_name,fields",
    CETACEAN_REPRESENTATIVE_ALLELES,
)
def test_parse_representative_cetacean_alleles(allele_name, species_prefix, gene_name, fields):
    allele = parse(allele_name)
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, species_prefix)
    eq_(allele.gene.name, gene_name)
    eq_(allele.allele_fields, fields)


def test_cela_old_prefix_round_trip():
    species = Species.get("CELA")
    assert species is not None
    eq_(species.name, "Cetacea sp.")

    allele = parse("Tutr-DQA*001:01:01")
    eq_(allele.to_string(use_old_species_prefix=True), "CELA-DQA*001:01:01")


def test_parse_historic_cela_input_uses_generic_species():
    gene = Gene.get("CELA", "DQA")
    assert gene is not None
    eq_(gene.species.prefix, "CELA")
    eq_(gene.mhc_class, "IIa")

    allele = parse("CELA-DQA*001:01:01")
    eq_(type(allele), Allele)
    eq_(allele.species.prefix, "CELA")
    eq_(allele.gene.name, "DQA")
    eq_(allele.allele_fields, ("001", "01", "01"))


# ---------------------------------------------------------------------------
# IPD designations preferred over generated forms (#146)
# ---------------------------------------------------------------------------

IPD_DESIGNATED = [
    ("Delphinapterus leucas", "Dele", "DeleLuca"),
    ("Neophocaena asiaeorientalis", "Neas", "NeopAsia"),
    ("Orcinus orca", "Oror", "OrciOrca"),
]


@pytest.mark.parametrize("latin_name,designated,generated", IPD_DESIGNATED)
def test_ipd_designation_is_the_canonical_prefix(latin_name, designated, generated):
    """
    These three carried a mhcgnomes-generated 4+4 as their canonical prefix
    while IPD-MHC's CeLA table designates a 2+2 that already resolved to them.
    So normalized output was a name we invented in preference to the published
    one. See #146.
    """
    species = Species.get_by_latin_name(latin_name)
    eq_(species.prefix, designated)
    eq_(species.prefix_provenance, "designated")
    assert generated in species.other_mhc_prefixes, f"{generated} stopped being an alias"


@pytest.mark.parametrize("latin_name,designated,generated", IPD_DESIGNATED)
def test_both_spellings_parse_and_normalize_to_the_designation(latin_name, designated, generated):
    for prefix in (designated, generated):
        result = parse(f"{prefix}-DQB1", raise_on_error=True)
        eq_(result.species.name, latin_name)
        eq_(result.to_string(), f"{designated}-DQB1")
