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

import re
from typing import Optional, Union

from .allele import Allele
from .class2_locus import Class2Locus
from .common import cache
from .errors import ParseError
from .gene import Gene
from .gene_class_info import GeneClassInfo
from .mhc_class import MhcClass
from .pair import Pair
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
from .species import Species, infer_species_from_context_only_prefix


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


def _reparse_with_context_only_prefix(
    parser: Parser,
    raw_string: str,
    expected_species: Species,
    infer_class2_pairing: bool,
    required_result_types,
    preferred_result_types,
    only_class1: bool,
    only_class2: bool,
    max_allele_fields,
):
    inferred = infer_species_from_context_only_prefix(raw_string)
    if inferred is None:
        return None
    candidate_species, matched_prefix = inferred
    if expected_species not in candidate_species:
        return None
    rewritten = f"{expected_species.prefix}{raw_string[len(matched_prefix) :]}"
    reparsed = parser.parse(
        rewritten,
        default_species=expected_species,
        infer_class2_pairing=infer_class2_pairing,
        raise_on_error=False,
        required_result_types=required_result_types,
        preferred_result_types=preferred_result_types,
        only_class1=only_class1,
        only_class2=only_class2,
        max_allele_fields=max_allele_fields,
    )
    if reparsed is None:
        return None
    return reparsed.copy(raw_string=raw_string)


def _format_species_options(species_objects, max_items=4):
    names = [sp.name for sp in species_objects]
    shown = names[:max_items]
    if len(names) > max_items:
        shown.append(f"+{len(names) - max_items} more")
    return ", ".join(shown)


def _format_canonical_prefix_options(species_objects, max_items=4):
    shown = [f"{sp.prefix} ({sp.name})" for sp in species_objects[:max_items]]
    if len(species_objects) > max_items:
        shown.append(f"+{len(species_objects) - max_items} more")
    return ", ".join(shown)


def _context_only_prefix_error_message(raw_string: str):
    inferred = infer_species_from_context_only_prefix(raw_string)
    if inferred is None:
        return None

    candidate_species, matched_prefix = inferred
    candidate_species = list(candidate_species)
    canonical_options = _format_canonical_prefix_options(candidate_species)
    global_owner = Species.get(matched_prefix)

    if global_owner is not None:
        return (
            f"Prefix '{matched_prefix}' is also used in source data for "
            f"{_format_species_options(candidate_species)}. "
            f"Runtime keeps '{matched_prefix}' for '{global_owner.name}'. "
            f"Use species='<latin name>' or a collision-free canonical prefix such as "
            f"{canonical_options}."
        )

    return (
        f"Prefix '{matched_prefix}' is source-attested for multiple species "
        f"({_format_species_options(candidate_species)}) and is not globally unique. "
        f"Use species='<latin name>' or a collision-free canonical prefix such as "
        f"{canonical_options}."
    )


_NON_MHC_REGION_GENE_NAMES = {
    "ABCB2": "TAP1",
    "ABCB3": "TAP2",
    "B2M": "B2M",
    "CIITA": "CIITA",
    "HAM1": "TAP1",
    "HAM2": "TAP2",
    "HM13": "HM13",
    "PRR3": "PRR3",
    "PSF1": "TAP1",
    "PSF2": "TAP2",
    "RING11": "TAP2",
    "RING4": "TAP1",
    "TAP-L": "TAP-L",
    "TAPL": "TAP-L",
    "TAP1": "TAP1",
    "TAP2": "TAP2",
    "TAPBP": "TAPBP",
}

_LENIENT_GENE_SUFFIX_RULES = {
    "A-U": ("I", "alpha"),
    "BLB": ("IIa", "beta"),
    "DAA": ("IIa", "alpha"),
    "DAB": ("IIa", "beta"),
    "DMA": ("IIb", "alpha"),
    "DMB": ("IIb", "beta"),
    "DNB": ("IIa", "beta"),
    "DPA1": ("IIa", "alpha"),
    "DQB1": ("IIa", "beta"),
    "DRA": ("IIa", "alpha"),
    "DR-1": ("IIa", "alpha"),
    "DXB": ("IIa", "beta"),
    "E-S": ("I", "alpha"),
    "F10": ("I", "alpha"),
    "M": ("IIa", "alpha"),
    "M1": ("IIa", "beta"),
    "Q10": ("I", "alpha"),
    "Q9": ("I", "alpha"),
    "U": ("I", "alpha"),
    "UA": ("I", "alpha"),
    "UAA": ("I", "alpha"),
    "UB": ("I", "alpha"),
}

_LENIENT_GENE_SUFFIX_PATTERNS = (
    (re.compile(r"^DAB\d+$", re.IGNORECASE), ("IIa", "beta")),
    (re.compile(r"^DRB\d+(?:-\d+)?$", re.IGNORECASE), ("IIa", "beta")),
)


def _chain_for_species_gene(species: Species, gene_name: str, mhc_class: Optional[str]):
    if mhc_class is None or mhc_class == "other":
        return None
    if mhc_class in {"I", "Ia", "Ib", "Ic", "Id"}:
        return "alpha"
    return species.class2_gene_name_to_chain_type.get(gene_name)


def _build_gene_class_info_from_parsed(parsed: Result, raw_string: str):
    if parsed is None:
        return None

    if isinstance(parsed, Allele):
        gene_name = parsed.gene.name
        mhc_class = parsed.mhc_class
        return GeneClassInfo(
            species=parsed.species,
            gene_name=gene_name,
            mhc_class=mhc_class,
            chain=_chain_for_species_gene(parsed.species, gene_name, mhc_class),
            non_mhc=mhc_class == "other",
            source="parsed_allele",
            raw_string=raw_string,
        )

    if isinstance(parsed, Gene):
        gene_name = parsed.name
        mhc_class = parsed.mhc_class
        return GeneClassInfo(
            species=parsed.species,
            gene_name=gene_name,
            mhc_class=mhc_class,
            chain=_chain_for_species_gene(parsed.species, gene_name, mhc_class),
            non_mhc=mhc_class == "other",
            source="parsed_gene",
            raw_string=raw_string,
        )

    if isinstance(parsed, Class2Locus):
        return GeneClassInfo(
            species=parsed.species,
            gene_name=parsed.name,
            mhc_class=parsed.mhc_class,
            chain=None,
            non_mhc=False,
            source="parsed_locus",
            raw_string=raw_string,
        )

    if isinstance(parsed, Pair):
        return GeneClassInfo(
            species=parsed.species,
            gene_name=f"{parsed.alpha.gene_name}/{parsed.beta.gene_name}",
            mhc_class=parsed.mhc_class,
            chain=None,
            non_mhc=False,
            source="parsed_pair",
            raw_string=raw_string,
        )

    if isinstance(parsed, MhcClass):
        return GeneClassInfo(
            species=parsed.species,
            gene_name=None,
            mhc_class=parsed.mhc_class,
            chain=parsed.chain,
            non_mhc=parsed.mhc_class == "other",
            source="parsed_class",
            raw_string=raw_string,
        )

    return None


def _normalize_inference_gene_token(gene_token: str):
    return gene_token.strip().strip(",;").upper()


def _strip_gene_token(candidate_gene_string: str):
    candidate_gene_string = candidate_gene_string.strip()
    if not candidate_gene_string:
        return None
    if any(ch.isspace() for ch in candidate_gene_string):
        return None
    candidate_gene_string = candidate_gene_string.split("/", 1)[0]
    candidate_gene_string = candidate_gene_string.split("*", 1)[0]
    candidate_gene_string = candidate_gene_string.split("#", 1)[0]
    candidate_gene_string = candidate_gene_string.strip(" -_.:;")
    if not candidate_gene_string:
        return None
    return candidate_gene_string


def _extract_species_and_gene_string(
    raw_string: str,
    parser: Parser,
    expected_species: Optional[Species],
):
    explicit_species, remaining = parser.parse_species_from_prefix(raw_string)
    if explicit_species is not None:
        if expected_species is not None and explicit_species != expected_species:
            return (
                None,
                None,
                (
                    f"Input prefix selects species '{explicit_species.name}', "
                    f"not requested species '{expected_species.name}'."
                ),
            )
        return explicit_species if expected_species is None else expected_species, remaining, None

    inferred = infer_species_from_context_only_prefix(raw_string)
    if inferred is not None:
        candidate_species, matched_prefix = inferred
        if expected_species is None:
            return None, None, _context_only_prefix_error_message(raw_string)
        if expected_species not in candidate_species:
            return (
                None,
                None,
                (
                    f"Prefix '{matched_prefix}' is not source-attested for "
                    f"'{expected_species.name}'."
                ),
            )
        remaining = raw_string[len(matched_prefix) :]
        return expected_species, remaining, None

    if expected_species is not None:
        return expected_species, raw_string, None

    return None, raw_string, None


def _infer_gene_rule(gene_token: str):
    normalized = _normalize_inference_gene_token(gene_token)
    if normalized in _LENIENT_GENE_SUFFIX_RULES:
        mhc_class, chain = _LENIENT_GENE_SUFFIX_RULES[normalized]
        return normalized, mhc_class, chain
    for regex, (mhc_class, chain) in _LENIENT_GENE_SUFFIX_PATTERNS:
        if regex.fullmatch(normalized):
            return normalized, mhc_class, chain
    return None


def _build_gene_class_info_from_family(species: Species, gene_token: str, raw_string: str):
    family_name = species.find_matching_gene_family_name(gene_token)
    if family_name is None:
        return None

    member_names = species.get_gene_family_members(family_name)
    member_classes = {species.get_mhc_class_of_gene(member_name) for member_name in member_names}
    if len(member_classes) != 1:
        return None
    mhc_class = member_classes.pop()

    member_chains = {
        _chain_for_species_gene(species, member_name, mhc_class) for member_name in member_names
    }
    chain = member_chains.pop() if len(member_chains) == 1 else None
    return GeneClassInfo(
        species=species,
        gene_name=family_name,
        mhc_class=mhc_class,
        chain=chain,
        non_mhc=mhc_class == "other",
        source="ontology_family",
        raw_string=raw_string,
    )


def _build_gene_class_info_from_token(species: Species, gene_token: str, raw_string: str):
    canonical_gene_name = species.find_matching_gene_name(gene_token)
    if canonical_gene_name is not None:
        mhc_class = species.get_mhc_class_of_gene(canonical_gene_name)
        return GeneClassInfo(
            species=species,
            gene_name=canonical_gene_name,
            mhc_class=mhc_class,
            chain=_chain_for_species_gene(species, canonical_gene_name, mhc_class),
            non_mhc=mhc_class == "other",
            source="canonical_gene",
            raw_string=raw_string,
        )

    locus = Class2Locus.get(species, gene_token)
    if locus is not None:
        return GeneClassInfo(
            species=species,
            gene_name=locus.name,
            mhc_class=locus.mhc_class,
            chain=None,
            non_mhc=False,
            source="canonical_locus",
            raw_string=raw_string,
        )

    family_info = _build_gene_class_info_from_family(species, gene_token, raw_string)
    if family_info is not None:
        return family_info

    normalized = _normalize_inference_gene_token(gene_token)
    if normalized in _NON_MHC_REGION_GENE_NAMES:
        return GeneClassInfo(
            species=species,
            gene_name=_NON_MHC_REGION_GENE_NAMES[normalized],
            mhc_class="other",
            chain=None,
            non_mhc=True,
            source="non_mhc_name",
            raw_string=raw_string,
        )

    inferred = _infer_gene_rule(gene_token)
    if inferred is not None:
        normalized_name, mhc_class, chain = inferred
        return GeneClassInfo(
            species=species,
            gene_name=normalized_name,
            mhc_class=mhc_class,
            chain=chain,
            non_mhc=False,
            source="heuristic_suffix",
            raw_string=raw_string,
        )

    return None


def parse_gene_class(
    raw_string: str,
    default_species=DEFAULT_SPECIES_PREFIX,
    species: Union[str, None] = None,
    raise_on_error: bool = True,
) -> Optional[GeneClassInfo]:
    """
    Leniently infer the MHC class/chain for gene-like inputs.

    This function first attempts the normal strict parser. If that fails, it
    falls back to species-aware gene-token inference for source-backed suffixes
    such as ``F10`` or ``DR-1`` and for known non-MHC-region helper genes like
    ``CIITA`` or ``TAP1``. Exact ontology-backed family names such as ``TAP``
    can be classified without inventing a specific member gene.
    """
    expected_species = Species.get(species) if species is not None else None
    if species is not None and expected_species is None:
        if raise_on_error:
            raise ParseError(f"Unknown species '{species}'")
        return None

    parsed = parse(
        raw_string,
        default_species=default_species,
        species=species,
        raise_on_error=False,
    )
    info = _build_gene_class_info_from_parsed(parsed, raw_string)
    if info is not None:
        return info

    parser = cached_parser()
    inferred_species, candidate_gene_string, error_message = _extract_species_and_gene_string(
        raw_string=raw_string,
        parser=parser,
        expected_species=expected_species,
    )
    if error_message is not None:
        if raise_on_error:
            raise ParseError(error_message)
        return None

    # Heuristic inference should only run when the caller supplied a strict
    # species or when the raw string carried an explicit species prefix.
    if inferred_species is None:
        if raise_on_error:
            raise ParseError(f"Could not infer MHC class from '{raw_string}'")
        return None

    candidate_gene_string = parser.strip_extra_chars(candidate_gene_string)
    gene_token = _strip_gene_token(candidate_gene_string)
    if gene_token is None:
        if raise_on_error:
            raise ParseError(f"Could not infer MHC class from '{raw_string}'")
        return None

    info = _build_gene_class_info_from_token(inferred_species, gene_token, raw_string)
    if info is not None:
        return info

    if raise_on_error:
        raise ParseError(f"Could not infer MHC class from '{raw_string}'")
    return None


def infer_mhc_class(
    raw_string: str,
    default_species=DEFAULT_SPECIES_PREFIX,
    species: Union[str, None] = None,
) -> Optional[str]:
    """
    Convenience wrapper around :func:`parse_gene_class` returning only the
    inferred MHC class string.
    """
    result = parse_gene_class(
        raw_string,
        default_species=default_species,
        species=species,
        raise_on_error=False,
    )
    if result is None:
        return None
    return result.mhc_class


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

    expected_species = Species.get(species) if species is not None else None
    effective_default = species if species is not None else default_species

    parser_error = None
    try:
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
    except ParseError as error:
        parser_error = error
        result = None

    if species is not None and expected_species is not None:
        rescued = _reparse_with_context_only_prefix(
            parser=parser,
            raw_string=raw_string,
            expected_species=expected_species,
            infer_class2_pairing=infer_class2_pairing,
            required_result_types=required_result_types,
            preferred_result_types=preferred_result_types,
            only_class1=only_class1,
            only_class2=only_class2,
            max_allele_fields=max_allele_fields,
        )
        if rescued is not None:
            result = rescued
            parser_error = None

    if parser_error is not None:
        maybe_context_message = (
            _context_only_prefix_error_message(raw_string) if species is None else None
        )
        if maybe_context_message is not None:
            raise ParseError(maybe_context_message) from parser_error
        raise parser_error

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
        expected = expected_species
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
