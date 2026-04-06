"""
Tests that natural-language phrases from papers containing MHC/HLA keywords
are correctly rejected as parse errors, not accidentally parsed as alleles,
genes, or species.
"""

import pytest

from mhcgnomes import parse

# Phrases that contain MHC keywords but are not allele names.
PAPER_PHRASES = [
    # Genetic phenomena
    "loss of heterozygosity in MHC",
    "MHC haplotype diversity",
    "HLA haploinsufficiency",
    "loss of HLA expression",
    "MHC class I downregulation",
    "MHC class II upregulation",
    "HLA loss of heterozygosity",
    # Biological processes
    "MHC-restricted T cell response",
    "MHC antigen presentation pathway",
    "MHC peptide binding groove",
    "HLA-mediated drug hypersensitivity",
    "MHC-dependent natural killer cell education",
    "cross-presentation by MHC class I",
    # Clinical / disease context
    "MHC-associated autoimmune disease",
    "HLA risk alleles for type 1 diabetes",
    "MHC region on chromosome 6",
    "the MHC locus is highly polymorphic",
    "HLA typing by next-generation sequencing",
    # Experimental methods
    "MHC tetramer staining",
    "HLA-matched donor selection",
    "MHC multimer assay",
    "pan-MHC class I antibody W6/32",
    # Evolution / comparative context
    "MHC evolution in teleost fish",
    "trans-species polymorphism at MHC loci",
    "MHC gene duplication in salmonids",
    "birth-and-death evolution of MHC genes",
    # Phrases with species prefixes embedded in non-allele context
    "Gaga BF locus structure",
    "Dare MHC class I gene family",
    "the Patr MHC region is syntenic with HLA",
    # Short misleading fragments
    # NB: "class I", "class II", "MHC I", "MHC II" intentionally parse as MhcClass results.
    "class I and class II",
    "beta-2 microglobulin",
    "antigen processing",
    "peptide loading complex",
    # Journal-style references
    "HLA nomenclature committee report 2024",
    "IPD-MHC database update",
    "IMGT/HLA release 3.51.0",
]


@pytest.mark.parametrize("phrase", PAPER_PHRASES)
def test_paper_phrase_does_not_parse(phrase):
    result = parse(phrase, raise_on_error=False)
    assert result is None, f"Expected None for {phrase!r}, got {result!r}"
