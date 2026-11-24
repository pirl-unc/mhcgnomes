"""Tests for mouse H2-IEg7 (#201) and non-human MHC gene/prefix gaps (#280)."""

import pytest

from mhcgnomes import Allele, Gene, Haplotype, Pair, parse

from .common import eq_

# ---------------------------------------------------------------------------
# 1. Mouse H2-IEg7 (#201)
# ---------------------------------------------------------------------------


def test_h2_ieg7_parses_as_eb_g7_allele_matching_ea_null_h2_ieb():
    """
    NOD (H2-g7) carries an H2-Ea promoter deletion (Ea: null; PMID 3003909) and
    a functional Eb*g7 allele (PMID 1975742, PMID 10352280). Like Ea-null H2-b
    (H2-IEb -> H2-EB*b), H2-IEg7 resolves to Allele(H2-EB*g7) rather than an
    empty Haplotype.
    """
    for raw in ("H2-IEg7", "H-2-IEg7"):
        res = parse(raw, raise_on_error=True)
        assert type(res) is Allele
        eq_(res.to_string(), "H2-EB*g7")
        eq_(res.mhc_class, "IIa")

    # With singleton collapse disabled, returns a populated locus-restricted Haplotype
    hap = parse("H2-IEg7", collapse_singleton_haplotypes=False, raise_on_error=True)
    assert type(hap) is Haplotype
    eq_(len(hap.alleles), 1)
    eq_(hap.alleles[0].to_string(), "H2-EB*g7")

    # Sibling I-A^g7 remains a Pair
    ia = parse("H2-IAg7", raise_on_error=True)
    assert type(ia) is Pair
    eq_(ia.to_string(), "H2-AA*d/AB*g7")


# ---------------------------------------------------------------------------
# 2. Redundant inner same-species prefix stripping (teleost/UniProt names)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_type,expected_species,expected_string",
    [
        ("OryziasLatipes-orla-uba", Gene, "Oryzias latipes", "OryzLati-UBA"),
        ("OryziasLatipes-orla-uaa", Gene, "Oryzias latipes", "OryzLati-UAA"),
        (
            "LabeobarbusIntermedius-MhcBain-DAB3-A02",
            Allele,
            "Labeobarbus intermedius",
            "LabeInte-DAB3*a02",
        ),
        ("AquaranaCatesbeiana-UA", Gene, "Lithobates catesbeianus", "LithCate-UA"),
        ("RanaCatesbeiana-UA", Gene, "Lithobates catesbeianus", "LithCate-UA"),
    ],
)
def test_double_prefixed_and_synonym_teleost_amphibian_genes(
    raw, expected_type, expected_species, expected_string
):
    res = parse(raw, raise_on_error=True)
    assert isinstance(res, expected_type)
    eq_(res.species.name, expected_species)
    eq_(res.to_string(), expected_string)


def test_cross_species_double_prefix_remains_rejected():
    assert parse("HLA-Mamu-A*01:01", raise_on_error=False) is None
    assert parse("OryziasLatipes-HLA-A*02:01", raise_on_error=False) is None


# ---------------------------------------------------------------------------
# 3. Non-human MHC gene loci and historic prefixes (#280)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected_species,expected_gene",
    [
        # Marsupials: opossum UI/UJ/UT1-UT17 & wallaby UO/Maeu-1/2/3
        ("Modo-UI", "Monodelphis domestica", "UI"),
        ("Modo-UJ", "Monodelphis domestica", "UJ"),
        ("Modo-UT1", "Monodelphis domestica", "UT1"),
        ("Modo-UT2", "Monodelphis domestica", "UT2"),
        ("Modo-UT4", "Monodelphis domestica", "UT4"),
        ("Modo-UT6", "Monodelphis domestica", "UT6"),
        ("Modo-UT9", "Monodelphis domestica", "UT9"),
        ("Modo-UT10", "Monodelphis domestica", "UT10"),
        ("Modo-UT15", "Monodelphis domestica", "UT15"),
        ("Modo-UT17", "Monodelphis domestica", "UT17"),
        ("NotaEuge-UO", "Notamacropus eugenii", "UO"),
        ("Maeu-UO", "Notamacropus eugenii", "UO"),
        ("Maeu-1", "Notamacropus eugenii", "1"),
        ("Maeu-2", "Notamacropus eugenii", "2"),
        ("Maeu-3", "Notamacropus eugenii", "3"),
        # Zebrafish L- and Z-lineage ZFIN names
        ("Dare-mhc1lla", "Danio rerio", "LLA"),
        ("Dare-mhc1lfa", "Danio rerio", "LFA"),
        ("Dare-mhc1zda", "Danio rerio", "ZDA"),
        ("Dare-mhc1zea", "Danio rerio", "ZEA"),
        # Rat RT1-M4 / Mill1 / Mill2
        ("RT1-M4", "Rattus sp.", "M4"),
        ("RT1.M4", "Rattus sp.", "M4"),
        ("Rano-Mill1", "Rattus norvegicus", "Mill1"),
        ("Rano-Mill2", "Rattus norvegicus", "Mill2"),
        # Mouse H2-M10.1..M10.6 dot notation
        ("H2-M10.1", "Mus musculus", "M10-1"),
        ("H2-M10.2", "Mus musculus", "M10-2"),
        ("H2-M10.3", "Mus musculus", "M10-3"),
        ("H2-M10.4", "Mus musculus", "M10-4"),
        ("H2-M10.5", "Mus musculus", "M10-5"),
        ("H2-M10.6", "Mus musculus", "M10-6"),
        # Deer mice Peromyscus class II A/E loci
        ("PeroMani-EB", "Peromyscus maniculatus", "EB"),
        ("PeroLeuc-EB", "Peromyscus leucopus", "EB"),
        ("PeroCali-EB", "Peromyscus californicus", "EB"),
        ("PeroMani-Aa", "Peromyscus maniculatus", "AA"),
        ("PeroErem-AB", "Peromyscus eremicus", "AB"),
        # Historic/synonym amphibian, cichlid, and penguin prefixes/genes
        ("Poch-UA", "Zhangixalus chenfui", "UA"),
        ("PochUA", "Zhangixalus chenfui", "UA"),
        ("Auha-DBA", "Aulonocara hansbaenschi", "DBA"),
        ("Auha-DAA2", "Aulonocara hansbaenschi", "DAA2"),
        ("Sphu-CLSI", "Spheniscus humboldti", "CLSI"),
        ("MhcSphu_CLSI", "Spheniscus humboldti", "CLSI"),
        ("Raya-beta1", "Lithobates yavapaiensis", "DAB"),
        ("ZhangixalusOmeimontis-Rhom-beta1", "Zhangixalus omeimontis", "DAB"),
        ("Rach-DRB", "Lithobates chiricahuensis", "DRB"),
        ("RachDRB", "Lithobates chiricahuensis", "DRB"),
    ],
)
def test_nonhuman_mhc_gene_and_prefix_gaps_280(raw, expected_species, expected_gene):
    res = parse(raw, raise_on_error=True)
    assert isinstance(res, Gene), f"{raw!r} parsed as {type(res).__name__}: {res!r}"
    eq_(res.species.name, expected_species)
    eq_(res.name, expected_gene)
