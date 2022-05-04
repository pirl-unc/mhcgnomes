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
    USE_ALLELE_ALIASES,
    GENE_SEPS,
    INFER_CLASS2_PAIRING,
    COLLAPSE_SINGLETON_HAPLOTYPES,
    COLLAPSE_SINGLETON_SEROTYPES,
)


@cache
def cached_parser(
        use_allele_aliases=USE_ALLELE_ALIASES,
        gene_seps=GENE_SEPS,
        collapse_singleton_haplotypes=COLLAPSE_SINGLETON_HAPLOTYPES,
        collapse_singleton_serotypes=COLLAPSE_SINGLETON_SEROTYPES,
        verbose=False):
    """
    Construct a Parser instance if this combination of arguments hasn't
    been used before, otherwise retrieve an existing parser.
    """
    return Parser(
        use_allele_aliases=use_allele_aliases,
        gene_seps=gene_seps,
        collapse_singleton_haplotypes=collapse_singleton_haplotypes,
        collapse_singleton_serotypes=collapse_singleton_serotypes,
        verbose=verbose)

def parse(
        raw_string,
        default_species=DEFAULT_SPECIES_PREFIX,
        use_allele_aliases=USE_ALLELE_ALIASES,
        infer_class2_pairing=INFER_CLASS2_PAIRING,
        collapse_singleton_haplotypes=COLLAPSE_SINGLETON_HAPLOTYPES,
        collapse_singleton_serotypes=COLLAPSE_SINGLETON_SEROTYPES,
        max_allele_fields=None,
        required_result_types=[],
        preferred_result_types=[],
        only_class1=False,
        only_class2=False,
        verbose=False,
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

    use_allele_aliases : bool

    infer_class2_pairing : bool
       If given only the alpha or beta chain of a Class II allele,
       try to infer the most likely pairing from population frequencies.

    collapse_singleton_haplotypes : bool
        If a Haplotype contains only a single allele or Class II allele pair,
        then return the allele instead of a haplotype.

    collapse_singleton_serotypes : bool
        If a Serotype contains only a single allele or Class II allele pair,
        then return the allele instead of a serotype.

    max_allele_fields : int
        If not None, restrict number of allele fields to given value.

    required_result_types : list of type
        Only return results of the given classes.

    preferred_result_types : list of type
        Return a result that's one of these classes if possible, otherwise None.

    only_class1 : bool
        Only return MHC Class I results

    only_class2 : bool
        Only return MHC Class II results

    verbose : bool
        Print intermediate parsing steps

    raise_on_error : bool
        Raise an exception if string can't be parsed. If False, return None
        instead.
    """
    parser = cached_parser(
        use_allele_aliases=use_allele_aliases,
        collapse_singleton_haplotypes=collapse_singleton_haplotypes,
        collapse_singleton_serotypes=collapse_singleton_serotypes,
        verbose=verbose)

    return parser.parse(
        raw_string,
        default_species=default_species,
        infer_class2_pairing=infer_class2_pairing,
        raise_on_error=raise_on_error,
        required_result_types=required_result_types,
        preferred_result_types=preferred_result_types,
        only_class1=only_class1,
        only_class2=only_class2,
        max_allele_fields=max_allele_fields)
