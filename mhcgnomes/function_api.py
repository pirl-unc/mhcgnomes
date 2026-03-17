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

from typing import Optional, Union

from .common import cache
from .errors import ParseError
from .parser import (
    COLLAPSE_SINGLETON_HAPLOTYPES,
    COLLAPSE_SINGLETON_SEROTYPES,
    DEFAULT_SPECIES_PREFIX,
    GENE_SEPS,
    INFER_CLASS2_PAIRING,
    USE_ALLELE_ALIASES,
    Parser,
)
from .result import Result
from .species import Species


@cache
def cached_parser(
    use_allele_aliases: bool = USE_ALLELE_ALIASES,
    gene_seps=GENE_SEPS,
    collapse_singleton_haplotypes: bool = COLLAPSE_SINGLETON_HAPLOTYPES,
    collapse_singleton_serotypes: bool = COLLAPSE_SINGLETON_SEROTYPES,
    verbose: bool = False,
) -> Parser:
    """
    Get or create a cached Parser instance.

    Construct a Parser instance if this combination of arguments hasn't
    been used before, otherwise retrieve an existing parser from cache.

    Parameters
    ----------
    use_allele_aliases : bool
        Whether to use allele alias mappings for parsing.
    gene_seps : tuple of str
        Separator characters between gene name and allele fields.
    collapse_singleton_haplotypes : bool
        If a Haplotype contains only a single allele, return the allele
        instead of a haplotype.
    collapse_singleton_serotypes : bool
        If a Serotype contains only a single allele, return the allele
        instead of a serotype.
    verbose : bool
        Print intermediate parsing steps for debugging.

    Returns
    -------
    Parser
        A Parser instance configured with the given options.

    Examples
    --------
    >>> parser = cached_parser()
    >>> result = parser.parse("HLA-A*02:01")
    >>> result.gene_name
    'A'
    """
    return Parser(
        use_allele_aliases=use_allele_aliases,
        gene_seps=gene_seps,
        collapse_singleton_haplotypes=collapse_singleton_haplotypes,
        collapse_singleton_serotypes=collapse_singleton_serotypes,
        verbose=verbose,
    )


def _reparse_result_for_species(
    parser: Parser,
    result: Result,
    expected_species: Species,
    infer_class2_pairing: bool,
    required_result_types,
    preferred_result_types,
    only_class1: bool,
    only_class2: bool,
    max_allele_fields,
):
    if type(result) is Species or not hasattr(result, "species"):
        return None

    speciesless_string = result.to_string(include_species=False)
    reparsed = parser.parse(
        f"{expected_species.prefix}-{speciesless_string}",
        default_species=expected_species,
        infer_class2_pairing=infer_class2_pairing,
        raise_on_error=False,
        required_result_types=required_result_types,
        preferred_result_types=preferred_result_types,
        only_class1=only_class1,
        only_class2=only_class2,
        max_allele_fields=max_allele_fields,
    )
    if reparsed is None or type(reparsed) is not type(result):
        return None
    if not hasattr(reparsed, "species") or reparsed.species != expected_species:
        return None
    return reparsed.copy(raw_string=result.raw_string)


def parse(
    raw_string: str,
    default_species=DEFAULT_SPECIES_PREFIX,
    species: Union[str, None] = None,
    use_allele_aliases: bool = USE_ALLELE_ALIASES,
    infer_class2_pairing: bool = INFER_CLASS2_PAIRING,
    collapse_singleton_haplotypes: bool = COLLAPSE_SINGLETON_HAPLOTYPES,
    collapse_singleton_serotypes: bool = COLLAPSE_SINGLETON_SEROTYPES,
    max_allele_fields=None,
    required_result_types=None,
    preferred_result_types=None,
    only_class1: bool = False,
    only_class2: bool = False,
    verbose: bool = False,
    raise_on_error: bool = True,
) -> Optional[Result]:
    """
    Parse MHC alleles into a structured representation.

    Parameters
    ----------
    raw_string : str
       String corresponding to allele, locus, or other MHC-related name

    default_species : str
       By default, parse alleles like "A*02:01" as human but it's possible
       to change this to some other species.

    species : str or None
       Strict species constraint. If provided, the final parse result must have
       this species exactly. Unlike default_species, this does not allow the
       parser to fall back to a different species when the input is explicit
       or ambiguous. If a non-Species result is first parsed at a generic
       ancestor taxon, it may be reparsed for the requested descendant species
       when that conversion is valid.

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
        Strict filter. Only return results of the given classes.

    preferred_result_types : list of type
        Prefer returning one of these classes when available.
        If none match, return the best non-preferred parse.

    only_class1 : bool
        Only return MHC Class I results

    only_class2 : bool
        Only return MHC Class II results

    verbose : bool
        Print intermediate parsing steps

    raise_on_error : bool
        Raise an exception if string can't be parsed. If False, return None
        instead.

    Returns
    -------
    Result
        A parsed MHC object, which may be an Allele, AlleleWithoutGene, Gene,
        Species, Haplotype, Serotype, Supertype, Pair, Class2Locus, or MhcClass
        depending on the input string. Returns None if parsing fails and
        raise_on_error is False.

    Raises
    ------
    ParseError
        If the string cannot be parsed and raise_on_error is True.

    Examples
    --------
    >>> from mhcgnomes import parse
    >>> allele = parse("HLA-A*02:01")
    >>> allele.gene_name
    'A'
    >>> allele.allele_fields
    ('02', '01')
    >>> allele.to_string()
    'HLA-A*02:01'
    """
    if preferred_result_types is None:
        preferred_result_types = []
    if required_result_types is None:
        required_result_types = []
    parser = cached_parser(
        use_allele_aliases=use_allele_aliases,
        collapse_singleton_haplotypes=collapse_singleton_haplotypes,
        collapse_singleton_serotypes=collapse_singleton_serotypes,
        verbose=verbose,
    )

    # species= is the strict form: the final result must have this species.
    # default_species= is the lenient form: used only when the string
    # doesn't specify a species.
    # They are mutually exclusive.
    if species is not None and default_species != DEFAULT_SPECIES_PREFIX:
        raise ValueError("Cannot specify both 'species' and 'default_species'")

    effective_default = species if species is not None else default_species

    result = parser.parse(
        raw_string,
        default_species=effective_default,
        infer_class2_pairing=infer_class2_pairing,
        raise_on_error=raise_on_error,
        required_result_types=required_result_types,
        preferred_result_types=preferred_result_types,
        only_class1=only_class1,
        only_class2=only_class2,
        max_allele_fields=max_allele_fields,
    )

    # Strict species check: if species= was provided, the final result must
    # have that exact species.
    #
    # Rules:
    # - Species results: exact match only.
    # - Non-Species results with .species: allow ancestor→descendant conversion
    #   only when reparsing under the requested descendant species succeeds.
    # - Descendant→ancestor conversion is never allowed.
    # - Results without .species: always pass.
    if species is not None and result is not None:
        expected = Species.get(species)
        if expected is None:
            # species= was provided but doesn't resolve to a known species.
            # This is always an error — we can't validate against an unknown species.
            if raise_on_error:
                raise ParseError(f"Unknown species '{species}' passed to species= parameter")
            return None
        else:
            if type(result) is Species:
                matches_expected = result == expected
            elif hasattr(result, "species"):
                result_species = result.species
                if result_species == expected:
                    matches_expected = True
                elif result_species.is_ancestor_of(expected):
                    converted = _reparse_result_for_species(
                        parser=parser,
                        result=result,
                        expected_species=expected,
                        infer_class2_pairing=infer_class2_pairing,
                        required_result_types=required_result_types,
                        preferred_result_types=preferred_result_types,
                        only_class1=only_class1,
                        only_class2=only_class2,
                        max_allele_fields=max_allele_fields,
                    )
                    if converted is not None:
                        result = converted
                        matches_expected = True
                    else:
                        matches_expected = False
                else:
                    matches_expected = False
            else:
                matches_expected = True

            if not matches_expected:
                parsed_species = (
                    result.name
                    if type(result) is Species
                    else getattr(result.species, "name", None)
                )
                if raise_on_error:
                    raise ParseError(
                        f"Parsed species '{parsed_species}' does not match "
                        f"expected species '{expected.name}' for '{raw_string}'"
                    )
                return None

    return result
