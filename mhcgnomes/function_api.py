# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .common import cache
from .parser import Parser
from .parser import (
    DEFAULT_SPECIES_PREFIX,
    MAP_ALLELE_ALIASES,
    GENE_SEPS,
    INFER_CLASS2_PAIRING,
    COLLAPSE_SINGLETON_HAPLOTYPES,
    COLLAPSE_SINGLETON_SEROTYPES,
)


@cache
def cached_parser(
        map_allele_aliases=MAP_ALLELE_ALIASES,
        gene_seps=GENE_SEPS,
        collapse_singleton_haplotypes=COLLAPSE_SINGLETON_HAPLOTYPES,
        collapse_singleton_serotypes=COLLAPSE_SINGLETON_SEROTYPES):
    """
    Construct a Parser instance if this combination of arguments hasn't
    been used before, otherwise retrieve an existing parser.
    """
    return Parser(
        map_allele_aliases=map_allele_aliases,
        gene_seps=gene_seps,
        collapse_singleton_haplotypes=collapse_singleton_haplotypes,
        collapse_singleton_serotypes=collapse_singleton_serotypes)

def parse(
        raw_string,
        default_species=DEFAULT_SPECIES_PREFIX,
        map_allele_aliases=MAP_ALLELE_ALIASES,
        infer_class2_pairing=INFER_CLASS2_PAIRING,
        simplify_haplotypes_if_possible=COLLAPSE_SINGLETON_HAPLOTYPES,
        raise_on_error=True):
    """
    Parse MHC alleles into a structured representation.

    Parameters
    ----------
    raw_string : str
       String corresponding to allele, locus, or other MHC-related name

    default_species : str
       By default, parse alleles like "A*02:01" as human but it's possible
       to change this to some other species.

    map_allele_aliases : bool

    infer_class2_pairing : bool
       If given only the alpha or beta chain of a Class II allele,
       try to infer the most likely pairing from population frequencies.

    simplify_haplotypes_if_possible : bool
        If a Haplotype contains only a single allele or Class II allele pair,
        then return the allele instead of a haplotype.

    raise_on_error : bool
        Raise an exception if string can't be parsed. If False, return None
        instead.
    """
    parser = cached_parser(
        map_allele_aliases=map_allele_aliases,
        collapse_singleton_haplotypes=simplify_haplotypes_if_possible)

    return parser.parse(
        raw_string,
        default_species=default_species,
        infer_class2_pairing=infer_class2_pairing,
        raise_on_error=raise_on_error)

def normalized_string(
        raw_string,
        include_species_prefix=True,
        use_old_species_prefix=False,
        map_allele_aliases=True,
        simplify_haplotypes_if_possible=COLLAPSE_SINGLETON_HAPLOTYPES,
        infer_class2_pairing=True,
        default_species="HLA",
        raise_on_error=True):
    """
    Transform MHC alleles into a canonical string representation.

    Examples:
        A2 -> HLA-A2
        A0201 -> HLA-A*02:01
        H2-K-k -> H2-Kk
        RT-1*9.5:f -> RT1-9.5f
        DRB1_0101 -> HLA-DRB1*01:01

    Parameters
    ----------
    raw_string : str
        String corresponding to allele, locus, or other MHC-related name

    include_species_prefix : bool
        Include species in the normalized. If False, then you would
        get "A*02:01" for "A0201", instead of "HLA-A*02:01"

    use_old_species_prefix : bool
        For species which have a newer four-digit code and and older locus
        name (such as "Ecqa" / "ELA"), use the older species prefix in the
        result.

    map_allele_aliases : bool

    simplify_haplotypes_if_possible : bool
        If a Haplotype contains only a single allele or Class II allele pair,
        then return the allele instead of a haplotype.

    infer_class2_pairing : bool
        If given only the alpha or beta chain of a Class II allele,
        try to infer the most likely pairing from population frequencies.

    default_species_prefix : str
        By default, parse alleles like "A*02:01" as human but it's possible
        to change this to some other species.

    raise_on_error : bool
        Raise an exception if string can't be parsed. If False, return None
        instead.
    """
    parsed_object = parse(
        raw_string,
        infer_class2_pairing=infer_class2_pairing,
        default_species=default_species,
        map_allele_aliases=map_allele_aliases,
        raise_on_error=raise_on_error,
        simplify_haplotypes_if_possible=simplify_haplotypes_if_possible)
    if not parsed_object:
        return None
    return parsed_object.to_string(
        include_species=include_species_prefix,
        use_old_species_prefix=use_old_species_prefix)

def compact_string(
        raw_string,
        use_old_species_prefix=False,
        map_allele_aliases=True,
        simplify_haplotypes_if_possible=COLLAPSE_SINGLETON_HAPLOTYPES,
        infer_class2_pairing=False,
        default_species="HLA",
        raise_on_error=True):
    """
    Turn HLA-A*02:01 into A0201 or H-2-D-b into H-2Db or
    HLA-DPA1*01:05-DPB1*100:01 into DPA10105-DPB110001

    Parameters
    ----------
    raw_string : str
        String corresponding to allele, locus, or other MHC-related name

    use_old_species_prefix : bool
        For species which have a newer four-digit code and and older locus
        name (such as "Ecqa" / "ELA"), use the older species prefix in the
        result.

    map_allele_aliases : bool

    simplify_haplotypes_if_possible : bool
        If a Haplotype contains only a single allele or Class II allele pair,
        then return the allele instead of a haplotype.


    infer_class2_pairing : bool
        If given only the alpha or beta chain of a Class II allele,
        try to infer the most likely pairing from population frequencies.

    default_species : str
        By default, parse alleles like "A*02:01" as human but it's possible
        to change this to some other species.

    raise_on_error : bool
        Raise an exception if string can't be parsed. If False, return None
        instead.
    """
    parsed_object = parse(
        raw_string,
        map_allele_aliases=map_allele_aliases,
        infer_class2_pairing=infer_class2_pairing,
        default_species=default_species,
        raise_on_error=raise_on_error,
        simplify_haplotypes_if_possible=simplify_haplotypes_if_possible)
    if not parsed_object:
        return None
    return parsed_object.compact_string(use_old_species_prefix=use_old_species_prefix)
