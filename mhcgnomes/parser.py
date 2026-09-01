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
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Optional, Union

from .allele import Allele
from .allele_annotations import (
    parse_annotations_from_allele_fields,
    parse_annotations_from_seq,
    valid_functional_annotations,
)
from .allele_without_gene import AlleleWithoutGene
from .ambiguous_alleles import AmbiguousAlleles
from .class2_locus import Class2Locus
from .common import cache, normalize_string, unique
from .data import haplotypes as raw_haplotypes_data
from .errors import ParseError
from .gene import Gene
from .haplotype import Haplotype
from .mhc_class import MhcClass
from .mutation import Mutation
from .non_mhc_genes import is_non_mhc_gene_name
from .pair import Pair, infer_class2_alpha_chain
from .parsing_helpers import (
    contains_any_letters,
    contains_whitespace,
    smart_split,
    split_allele_fields,
    split_digits_at_end,
    strip_whitespace_and_dashes,
)
from .result import Result
from .result_sorting import pick_best_result
from .result_with_species import ResultWithSpecies
from .serotype import Serotype
from .species import (
    Species,
    classify_species_source,
    find_matching_species_objects,
    infer_species_from_prefix,
    species_named_in,
)
from .standard_format import parse_standard_allele_format
from .supertype import Supertype
from .token import Token
from .tokenize import tokenize

# Regex for MHC region labels like MHCIIB, mhc2a, MHC-IA, mhc1, etc.
_MHC_REGION_RE = re.compile(
    r"^mhc[-_]?(I{1,3}|1|2)(a|b)?$",
    re.IGNORECASE,
)


def _names_context_only_gene(result):
    """
    Does this parse result rest on a gene that needs the species named first?

    See Species.gene_is_context_only: the gene is real, but the string is
    contested enough that it should not be handed to a caller who never said
    which species they meant.
    """
    gene = result if isinstance(result, Gene) else getattr(result, "gene", None)
    if gene is None or gene.species is None:
        return False
    return gene.species.gene_is_context_only(gene.name)


def _parse_mhc_region_label(seq):
    """
    Parse MHC region labels like MHCIIB, mhc2a, MHC-IA, mhc1.
    Returns (mhc_class_str, chain) or None.
    """
    m = _MHC_REGION_RE.match(seq.replace("-", ""))
    if m is None:
        return None
    class_part = m.group(1).upper()
    chain_letter = m.group(2)
    if class_part in ("1", "I"):
        mhc_class = "I"
    elif class_part in ("2", "II"):
        mhc_class = "II"
    else:
        return None
    if chain_letter is None:
        chain = None
    elif chain_letter.upper() == "A":
        chain = "alpha"
    elif chain_letter.upper() == "B":
        chain = "beta"
    else:
        return None
    return (mhc_class, chain)


_SINGLE_CHAR_FUNCTIONAL_ANNOTATIONS = "".join(
    sorted(annot for annot in valid_functional_annotations if len(annot) == 1)
)

# default values for Parser parameters, reused in the 'parse' function below
DEFAULT_SPECIES_PREFIX = "HLA"
USE_ALLELE_ALIASES = False
INFER_CLASS2_PAIRING = False
COLLAPSE_SINGLETON_HAPLOTYPES = True
COLLAPSE_SINGLETON_SEROTYPES = False
MAP_SPECIES_GROUP_TO_TOP_SPECIES = False
GENE_SEPS = "*_-^:."


# Strings which mean "no value" but which would otherwise parse as something
# real. Only the "n/a" family needs listing here: other null markers such as
# "na", "nd", "none" and "unknown" already match nothing in the ontology.
NULL_VALUE_STRINGS = frozenset({"n/a"})


class Parser:
    """
    Parser for MHC nomenclature strings.

    The Parser class handles parsing of MHC allele names, gene names, species
    prefixes, haplotypes, serotypes, and other MHC-related nomenclature across
    multiple species.

    For most use cases, the module-level :func:`parse` function is simpler
    to use than instantiating a Parser directly.

    Parameters
    ----------
    use_allele_aliases : bool, default False
        Convert old allele aliases to newer names.
    map_species_group_to_top_species : bool, default False
        Map species group prefixes to the primary species.
    collapse_singleton_haplotypes : bool, default True
        If a haplotype contains a single allele, return the allele directly.
    collapse_singleton_serotypes : bool, default False
        If a serotype contains a single allele, return the allele directly.
    gene_seps : str, default "*_-^:."
        Characters that can separate gene name from allele fields.
    verbose : bool, default False
        Print intermediate parsing steps for debugging.

    Examples
    --------
    >>> parser = Parser()
    >>> result = parser.parse("HLA-A*02:01")
    >>> result.gene_name
    'A'
    """

    def __init__(
        self,
        use_allele_aliases: bool = USE_ALLELE_ALIASES,
        map_species_group_to_top_species: bool = MAP_SPECIES_GROUP_TO_TOP_SPECIES,
        collapse_singleton_haplotypes: bool = COLLAPSE_SINGLETON_HAPLOTYPES,
        collapse_singleton_serotypes: bool = COLLAPSE_SINGLETON_SEROTYPES,
        gene_seps: Sequence[str] = GENE_SEPS,
        verbose=False,
    ):
        """
        use_allele_aliases : bool
            Convert old allele aliases to newer names. For example,
            change "SLA-2*07we01" to "SLA-2*07:03"

        map_species_group_to_top_species : bool

        gene_seps : iterable of str
            Possible separators used after gene names

        collapse_singleton_haplotypes : bool
            If a haplotype contains just a single allele (or Class II pair),
            return that allele instead of the haplotype.

        collapse_singleton_serotypes : bool
            If a serotype contains just one allele, return that instead of
            the Serotype object containing it.

        verbose : bool
            Print the parse candidates for every distinct token
        """
        self.use_allele_aliases = use_allele_aliases
        self.map_species_group_to_top_species = map_species_group_to_top_species
        self.collapse_singleton_haplotypes = collapse_singleton_haplotypes
        self.collapse_singleton_serotypes = collapse_singleton_serotypes
        self.gene_seps = gene_seps
        self.verbose = verbose

        # technically we could just wrap the transform method with @cache
        # but since it's called a lot it's faster to make a dedicated cache
        # for a single input argument
        self._transform_cache = {}

    def parse_species_from_prefix(self, name: str):
        """
        Returns tuple with two elements:
            - Species
            - remaining string after species prefix
        """
        species_and_original_prefix = infer_species_from_prefix(name)
        if species_and_original_prefix is None:
            return None, name
        species, original_prefix = species_and_original_prefix
        original_prefix_length = len(original_prefix)
        remaining_string = name[original_prefix_length:]
        return species, remaining_string

    @staticmethod
    def _species_of(result):
        """The species a result is about, whatever its type."""
        if type(result) is Species:
            return result
        return getattr(result, "species", None)

    def species_named_in(self, name: str):
        """Which species, if any, the input string names outright."""
        return species_named_in(name)

    def classify_species_source(
        self,
        name: str,
        result,
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
    ):
        """
        Returns "explicit", "inferred", "default", or None -- see
        Result.species_source.
        """
        return classify_species_source(name, self._species_of(result), default_species)

    def parse_species(self, name: str, default_species: Union[Species, str, None] = None):
        """
        Returns tuple with elements:
            - Species
            - remaining string after species prefix
        """
        (species, remaining_string) = self.parse_species_from_prefix(name)

        if species is None:
            if default_species:
                species = Species.get(default_species)
            else:
                species = None
        remaining_string = self.strip_extra_chars(remaining_string)
        return species, remaining_string

    def _resolve_unparsed_allele_alias(self, name: str, default_species: Union[Species, str, None]):
        """Resolve an exact alias whose source spelling cannot otherwise be parsed."""
        species, name_without_species = self.parse_species(name, default_species=default_species)
        if species is None:
            return None

        current_name = name_without_species
        visited = set()
        while current_name in species.allele_aliases:
            normalized_name = normalize_string(current_name)
            if normalized_name in visited:
                raise ValueError(
                    f"Cyclic allele alias for {species.prefix}: {name_without_species}"
                )
            visited.add(normalized_name)
            current_name = species.allele_aliases[current_name]

        if not visited:
            return None
        return species, current_name

    def _find_matching_name_and_parse_alleles(
        self, query_name: str, name_to_alleles_dict: Mapping[str, Sequence[str]], species: Species
    ):
        """
        Factoring out this function since it's shared between
        Haplotype and Serotype

        Returns (str, list of Allele) or None
        """
        gene_aliases_dict = species.gene_aliases

        candidate_names = [query_name]
        lower = query_name.lower()
        for old_gene_name, new_gene_name in gene_aliases_dict.items():
            old_name_lower = old_gene_name.lower()
            if lower.startswith(old_name_lower):
                candidate_names.append(new_gene_name + query_name[len(old_gene_name) :])

        allele_names = None
        for candidate_name in candidate_names:
            if candidate_name in name_to_alleles_dict:
                allele_names = name_to_alleles_dict[candidate_name]
                normalized_name = name_to_alleles_dict.original_key(candidate_name)
                break

        if allele_names is None:
            return None

        alleles = []
        for allele_name in allele_names:
            candidates = self.parse_allele_or_gene_candidates(
                species, str_after_species=allele_name
            )

            allele = pick_best_result(candidates, raise_on_error=False)
            if allele is None:
                print(
                    f"Warning: unable to parse allele name '{allele_name}' for '{normalized_name}'"
                )
            else:
                alleles.append(allele)
        return (normalized_name, alleles)

    def get_serotype(self, species: Union[Species, str], serotype_name: str):
        """
        Getting around potential circular dependency between Parser and
        Serotype by not having a Serotype.get method and parsing a Serotype's
        associated allele names here (in the Parser object).

        Returns Serotype or None
        """
        species = Species.get(species)

        if species is None:
            return None

        name_and_alleles = self._find_matching_name_and_parse_alleles(
            query_name=serotype_name, name_to_alleles_dict=species.serotypes, species=species
        )

        if name_and_alleles is None:
            return None

        normalized_name, alleles = name_and_alleles

        return Serotype(
            species=species, name=normalized_name, alleles=alleles, raw_string=serotype_name
        )

    def get_heterodimer(self, species: Union[Species, str], heterodimer_name: str):
        """
        Look up a heterodimer shorthand name (e.g., DQ2.5) and return a Pair object.

        Heterodimer shorthand notation is commonly used for HLA-DQ molecules:
        - DQ2.5 = DQA1*05:01/DQB1*02:01
        - DQ2.2 = DQA1*02:01/DQB1*02:02
        etc.

        Returns Pair or None
        """
        species = Species.get(species)

        if species is None:
            return None

        # Look up the heterodimer name in the species' heterodimers dictionary
        heterodimer_info = species.heterodimers.get(heterodimer_name)
        if heterodimer_info is None:
            return None

        # Get alpha and beta allele names
        alpha_name = heterodimer_info.get("alpha")
        beta_name = heterodimer_info.get("beta")

        if not alpha_name or not beta_name:
            return None

        # Parse the alpha and beta alleles
        alpha_allele = self.parse(
            alpha_name, default_species=species, infer_class2_pairing=False, raise_on_error=False
        )
        beta_allele = self.parse(
            beta_name, default_species=species, infer_class2_pairing=False, raise_on_error=False
        )

        if alpha_allele is None or beta_allele is None:
            return None

        # Create and return a Pair object
        return Pair.get(alpha_allele, beta_allele, raw_string=heterodimer_name)

    def get_supertype(self, species: Union[Species, str], supertype_name: str):
        """
        Look up a supertype name (e.g., "A02", "B07") and return a Supertype object.

        HLA class I supertypes are functional groupings of alleles that share
        peptide binding properties. The nine major supertypes (A01, A02, A03,
        A24, B07, B08, B27, B44, B58, B62) were defined by Sidney et al. 2008.

        Supertype names can be specified with or without leading zeros:
        - "A2" or "A02" -> A02 supertype
        - "B7" or "B07" -> B07 supertype

        Returns Supertype or None
        """
        species = Species.get(species)

        if species is None:
            return None

        # Try to find the supertype in the dictionary
        # The NormalizingDictionary will handle case-insensitivity
        supertype_info = species.supertypes.get(supertype_name)
        matched_name = supertype_name

        # Try normalizing: add leading zero if single digit (A2 -> A02)
        if supertype_info is None and len(supertype_name) >= 2:
            letter = supertype_name[0]
            number = supertype_name[1:]
            if number.isdigit() and len(number) == 1:
                normalized_name = f"{letter}0{number}"
                supertype_info = species.supertypes.get(normalized_name)
                if supertype_info is not None:
                    matched_name = normalized_name

        if supertype_info is None:
            return None

        # Get the original (properly-cased) key from the dictionary
        canonical_name = species.supertypes.original_key(matched_name)

        # Get allele list and representative
        allele_names = supertype_info.get("alleles", [])
        representative_name = supertype_info.get("representative")

        # Parse alleles
        alleles = []
        for allele_name in allele_names:
            allele = self.parse(
                allele_name,
                default_species=species,
                infer_class2_pairing=False,
                raise_on_error=False,
            )
            if allele is not None:
                alleles.append(allele)

        # Parse representative allele
        representative = None
        if representative_name:
            representative = self.parse(
                representative_name,
                default_species=species,
                infer_class2_pairing=False,
                raise_on_error=False,
            )

        return Supertype(
            species=species,
            name=canonical_name,
            alleles=alleles,
            representative=representative,
            raw_string=supertype_name,
        )

    def parse_haplotype_with_class2_locus_from_any_string_split(
        self, species: Union[Species, str], locus_and_haplotype: str
    ):
        """
        Try parsing a string like "IAk" into the 'k' mouse haplotype restricted
        at the A locus
        """
        # Don't split strings that are directly in the species' gene list
        # (e.g. "AA" should remain Gene("AA"), not locus "A" + haplotype "a").
        # Use the gene_names set for exact (case-insensitive) matching,
        # avoiding Gene.get which strips MHC class prefixes like "I" from "IAb".
        species_obj = Species.get(species)
        if species_obj is not None and locus_and_haplotype in species_obj.gene_names:
            return None
        for locus_length in range(1, len(locus_and_haplotype)):
            locus_string = self.strip_extra_chars(locus_and_haplotype[:locus_length])
            locus = Class2Locus.get(species, locus_string)
            if locus is None:
                continue
            haplotype_string = self.strip_extra_chars(locus_and_haplotype[locus_length:])
            haplotype = self.get_haplotype(species, haplotype_string)
            if haplotype is None:
                continue
            haplotype = haplotype.restrict_class2_locus(class2_locus=locus, raise_on_error=False)
            if haplotype:
                return haplotype
        return None

    def get_haplotype(self, species: Union[Species, str], haplotype_name: str):
        """
        Getting around the potential circular dependency between Parser and
        Haplotype by not having a Haplotype.get function and only
        creating Haplotype objects in parser.

        Return Haplotype or None
        """
        species = Species.get(species)
        if species is None:
            return None

        name_and_alleles = self._find_matching_name_and_parse_alleles(
            query_name=haplotype_name, name_to_alleles_dict=species.haplotypes, species=species
        )

        if name_and_alleles is None:
            return None

        normalized_name, alleles = name_and_alleles

        return Haplotype(
            species=species, name=normalized_name, alleles=alleles, raw_string=haplotype_name
        )

    def create_crossed_haplotype(
        self, first_haplotype_object: Haplotype, second_haplotype_name: str
    ):
        if first_haplotype_object is None:
            return None
        if len(second_haplotype_name) == 0:
            return None
        if not second_haplotype_name.isalnum():
            return None
        second_haplotype_object = self.get_haplotype(
            first_haplotype_object.species, second_haplotype_name
        )

        if second_haplotype_object is None:
            return None
        name = f"{first_haplotype_object.name}/{second_haplotype_object.name}"
        raw_string = f"{first_haplotype_object.raw_string}/{second_haplotype_name}"
        return Haplotype(
            species=first_haplotype_object.species,
            name=name,
            alleles=first_haplotype_object.alleles + second_haplotype_object.alleles,
            raw_string=raw_string,
        )

    def parse_haplotype(
        self,
        haplotype_name: str,
        default_species: Union[Species, str, None] = None,
        strict_default_species: bool = False,
    ):
        # first try determining the species purley based on the string given
        # with reference to the default species
        species, remaining_string = self.parse_species(haplotype_name, default_species=None)
        if species:
            haplotype = self.get_haplotype(species, remaining_string)
            if haplotype:
                return haplotype

        # if this fails, try using the default species and also try
        # parsing the haplotype purely based on name
        matches = []
        species, remaining_string = self.parse_species(
            haplotype_name, default_species=default_species
        )

        if species:
            haplotype = self.get_haplotype(species, remaining_string)
            if haplotype:
                matches.append(haplotype)

        if strict_default_species and default_species is not None:
            default_species = Species.get(default_species)
            matches.extend(
                haplotype
                for haplotype in self.get_haplotypes_for_any_species(haplotype_name)
                if haplotype.species == default_species
            )
            if len(matches) == 0:
                return None
            return pick_best_result(matches)

        matches.extend(self.get_haplotypes_for_any_species(haplotype_name))

        if len(matches) == 0:
            return None
        return pick_best_result(matches)

    def get_haplotypes_for_any_species(self, haplotype_name: str) -> Sequence[Haplotype]:
        """
        Returns list of all haplotypes matching the given name
        """
        matches = []
        for species_name, haplotype_dict in raw_haplotypes_data.items():
            if haplotype_name in haplotype_dict:
                species, remaining_string = self.parse_species(species_name)
                if species is None or len(remaining_string) > 0:
                    continue
                normalized_name = haplotype_dict.original_key(haplotype_name)
                haplotype = self.get_haplotype(species, normalized_name)
                if haplotype:
                    matches.append(haplotype)
        return matches

    def parse_allele_from_allele_fields(
        self,
        gene: Gene,
        allele_fields: Union[str, Sequence[str], None],
        functional_annotations: Union[str, Sequence[str], None] = None,
        raw_string: Union[str, None] = None,
    ) -> Union[Gene, Allele, None]:
        if allele_fields is None:
            return None

        if len(allele_fields) == 0:
            return gene

        if functional_annotations is None:
            allele_fields, prefix_annotations, suffix_annotations = (
                parse_annotations_from_allele_fields(allele_fields)
            )
            functional_annotations = prefix_annotations + suffix_annotations

        if len(allele_fields) == 0 or len(allele_fields) > 4:
            return None

        # species specific heuristics currently going here but should eventually
        # go into a YAML configuration
        if gene.is_human and gene.mhc_class in {"Ia", "IIa"} and len(allele_fields) == 1:
            # don't parse allele groups like B*12 here since it's
            # too for these to beat haplotypes/serotypes in the ranking
            #
            # Still need to allow parsing of alleles like MICA*067
            return None

        for allele_field in allele_fields:
            # as far as I can tell, "*" and "-" never occur as part of an allele
            # name except as a sep after the gene
            if "*" in allele_field:
                return None
            if "-" in allele_field:
                return None
            if gene.is_human and not allele_field.isdigit():
                return None
            # chicken alleles look like "*19" or "*9.5" but shouldn't contain
            # letters
            if gene.is_chicken and not all((c.isdigit() or c == ".") for c in allele_field):
                return None
        return Allele.get_with_gene(
            gene, allele_fields, annotations=functional_annotations, raw_string=raw_string
        )

    def get_gene_or_locus(self, species: Union[Species, str], name: str):
        fns = [Gene.get, Class2Locus.get]
        for fn in fns:
            result = fn(species, name)
            if result:
                return result
        return None

    def parse_gene_candidates_from_prefixes(self, species: Union[Species, str], seq: str):
        """
        Parse genes such as "A" or "DQB" and collect them with
        remaining string.

        Returns list of (gene_name, str_after_gene) pairs.
        """
        results = []
        longest_exact_gene_with_annotation_suffix = 0
        for n in range(len(seq), 0, -1):
            substring = seq[:n]
            parsed = Gene.get(species, substring)
            if (
                parsed
                and self.strip_extra_chars(seq[n:]).lower()
                in _SINGLE_CHAR_FUNCTIONAL_ANNOTATIONS.lower()
            ):
                longest_exact_gene_with_annotation_suffix = n
                break
        for n in range(len(seq), 0, -1):
            substring = seq[:n]
            parsed = Gene.get(species, substring)
            if parsed:
                if longest_exact_gene_with_annotation_suffix > n and self.strip_extra_chars(
                    seq[n:]
                ):
                    continue
                results.append((parsed, seq[n:]))
        return results

    compact_gene_and_allele_regex = re.compile(r"([A-Za-z]+)([0-9:]+[A-Z]?)")
    generic_compact_allele_suffix_regex = re.compile(
        rf"\d+(?::\d+)*[{_SINGLE_CHAR_FUNCTIONAL_ANNOTATIONS}]?$", re.IGNORECASE
    )

    def strip_extra_chars(self, seq: str):
        for sep in self.gene_seps:
            while seq.startswith(sep):
                seq = seq[1:]
        return strip_whitespace_and_dashes(seq)

    def parse_gene_candidates(
        self, species: Union[Species, str], str_after_species: str
    ) -> Sequence[tuple[Gene, str]]:
        """
        Returns list of (Gene, remaining_string) pairs.
        """
        if contains_whitespace(str_after_species):
            return []

        # A curated non-MHC gene name is never split into a locus plus an
        # allele suffix. "Kdm5d" under a mouse species would otherwise become
        # H2-K*dm5d -- the real locus K, with everything after it read as an
        # allele -- and "Daxx" becomes H2-D*axx. Both look valid and get
        # dispatched onward, so the false positive is silent (#133).
        #
        # Only when the species does not declare the name itself: most entries
        # in that table (TAP1, TAPBP, B2M, ...) are real genes in the ontology
        # and must keep parsing.
        stripped_token = self.strip_extra_chars(str_after_species)
        if (
            is_non_mhc_gene_name(stripped_token)
            and species.find_matching_gene_name(stripped_token) is None
        ):
            return []

        candidates = []

        def add_to_candidates(gene_name, str_after_gene):
            str_after_gene = self.strip_extra_chars(str_after_gene)
            if len(gene_name) > 0:
                gene = Gene.get(species, gene_name)
                if gene:
                    candidates.append((gene, str_after_gene))

        if str_after_species.count("*") == 1:
            # if the sequence conforms to the "A*0201" format, then
            # just split on the '*' character and return this as the
            # only possibility
            gene_name, str_after_gene = smart_split(str_after_species, "*")
            add_to_candidates(gene_name, str_after_gene)
        else:
            # if we don't have the canonical format, then try three different
            # methods for identifying the gene name
            candidates.extend(
                self.parse_gene_candidates_from_prefixes(
                    species, self.strip_extra_chars(str_after_species)
                )
            )

            for sep in self.gene_seps:
                if str_after_species.count(sep) == 1:
                    gene_name, str_after_gene = smart_split(str_after_species, sep)
                    add_to_candidates(gene_name, str_after_gene)

            # If the string had neither "*" nor "_" then try to collect the gene
            # name as the non-numerical part at the start of the string.
            regex_match = Parser.compact_gene_and_allele_regex.fullmatch(str_after_species)
            if regex_match:
                gene_name, str_after_gene = regex_match.groups()
                longer_exact_gene = species.find_matching_gene_name(
                    self.strip_extra_chars(str_after_species[:-1])
                )
                if longer_exact_gene is None:
                    add_to_candidates(gene_name, self.strip_extra_chars(str_after_gene))
        return unique(candidates)

    def split_by_hyphen_except_gene_names(self, species, str_after_species):
        """
        Split a string into a list of parts by hyphens except keep
        gene names such as "M3-1" together
        """
        parts = str_after_species.split("-")
        parts_with_merged_gene_names = []
        i = 0
        while i < len(parts):
            first_part = parts[i]
            if i + 1 == len(parts):
                parts_with_merged_gene_names.append(first_part)
                break

            next_part = parts[i + 1]
            combined = f"{first_part}-{next_part}"
            if species.find_matching_gene_name(combined):
                parts_with_merged_gene_names.append(combined)
                i += 2
            else:
                parts_with_merged_gene_names.append(first_part)
                i += 1
        return parts_with_merged_gene_names

    def parse_allele_or_gene_candidates(self, species, str_after_species, raw_string=None):
        # try to heuristically split_token_sequences apart the gene name and any allele information
        # when the requires separators are missing
        # Examples which will parse correctly here:
        #   A*0201
        #   A*02:01
        #   A_0101
        #   A_01:01
        #   A-0101
        #   A-01:01
        # However this will not work:
        #   - A_01_01
        if contains_whitespace(str_after_species):
            return []
        candidate_results = []

        exact_gene = Gene.get(species, str_after_species)
        if exact_gene is not None:
            return [exact_gene]

        known_allele = species.get_known_allele(gene_name=None, allele_name=str_after_species)

        if known_allele is not None:
            gene_name, allele_name = known_allele
            assert gene_name is None
            if "*" not in allele_name:
                candidate_results.append(
                    AlleleWithoutGene.get(
                        species=species, name=allele_name, raw_string=str_after_species
                    )
                )

        for gene, allele_name in self.parse_gene_candidates(species, str_after_species):
            if gene is None:
                continue
            if len(allele_name) == 0:
                candidate_results.append(gene)
                continue

            if (
                "*" not in str_after_species
                and not any(sep in str_after_species for sep in self.gene_seps)
                and not self._compact_gene_suffix_can_be_allele(gene, allele_name)
            ):
                continue

            allele = self.parse_allele_with_gene(gene, allele_name, raw_string=raw_string)
            if allele:
                candidate_results.append(allele)
        return candidate_results

    def _compact_gene_suffix_can_be_allele(self, gene: Gene, allele_name: str) -> bool:
        allele_name = self.strip_extra_chars(allele_name)
        if not allele_name:
            return False
        if gene.species.is_mouse:
            return allele_name.isalnum() and not allele_name.isnumeric()
        if gene.species.is_rat:
            return allele_name.isalnum()
        if gene.species.is_pig:
            return True
        return Parser.generic_compact_allele_suffix_regex.fullmatch(allele_name) is not None

    def parse_allele_with_gene(
        self,
        gene: Gene,
        str_after_gene: str,
        preserve_caps: bool = False,
        raw_string: Union[str, None] = None,
    ):
        if gene is None:
            return None

        if not str_after_gene:
            return None

        if contains_whitespace(str_after_gene):
            return None

        if "*" in str_after_gene:
            return None

        str_after_gene = self.strip_extra_chars(str_after_gene)

        species = gene.species

        if species.is_mouse:
            if str_after_gene.isalnum() and not str_after_gene.isnumeric():
                # mouse alleles can be a mixture of numbers and letters
                # but can't be only numbers
                return Allele.get_with_gene(
                    gene,
                    str_after_gene if preserve_caps else str_after_gene.lower(),
                    raw_string=raw_string,
                )
            else:
                return None
        elif species.is_rat:
            return Allele.get_with_gene(
                gene,
                str_after_gene if preserve_caps else str_after_gene.lower(),
                raw_string=raw_string,
            )
        elif species.is_pig:
            # parse e.g. "SLA-3-US#11"
            if "#" in str_after_gene:
                return Allele.get_with_gene(
                    gene,
                    str_after_gene if preserve_caps else str_after_gene.upper(),
                    raw_string=raw_string,
                )
            elif contains_any_letters(str_after_gene):
                return Allele.get_with_gene(
                    gene,
                    str_after_gene if preserve_caps else str_after_gene.lower(),
                    raw_string=raw_string,
                )
        str_after_gene, prefix_annotations, functional_annotations = parse_annotations_from_seq(
            str_after_gene
        )
        # only allele names which allow three digits in second field seem to be
        # human class I names such as "HLA-B*15:120" but not Ic/Id genes
        # like MICA.
        # For human class II genes it seems like DPB1 is the only one using
        # three digits in the first field
        allow_three_digits_in_second_field = species.is_human and (
            gene.mhc_class in {"I", "Ia", "Ib"} or not gene.name.startswith("DP")
        )

        allow_three_digits_in_first_field = not allow_three_digits_in_second_field
        allele_fields = split_allele_fields(
            str_after_gene=str_after_gene,
            allow_three_digits_in_first_field=allow_three_digits_in_first_field,
            allow_three_digits_in_second_field=allow_three_digits_in_second_field,
        )

        if allele_fields:
            # for now we only expect a "W" prefix annotation, indicating
            # that it's a workshop allele, so we just put that back in the
            # sequence.
            first_field = "".join(prefix_annotations) + allele_fields[0]
            allele_fields = (first_field, *tuple(allele_fields[1:]))
            return self.parse_allele_from_allele_fields(
                gene=gene,
                allele_fields=allele_fields,
                functional_annotations=functional_annotations,
                raw_string=raw_string,
            )
        else:
            return None

    def parse_class2_pair_with_hyphen_sep(self, species, str_after_species):
        """
        If possible, try parsing allele pair with a single hyphen separator,
        e.g. DRA1*01:01-DRB1*01:01
        """
        hyphen_parts = self.split_by_hyphen_except_gene_names(species, str_after_species)

        if len(hyphen_parts) == 2:
            # this situation is tricky since it might be either
            # a class II allele pair
            #   e.g. DRA1*01:01-DRB1*01:01
            # or a class I allele where '-' is used instead of '*'
            #   e.g. 1-HB01 (swine allele)
            alpha, beta = hyphen_parts
            return self.parse_class2_pair_from_alpha_and_beta_strings(
                alpha, beta, default_species=species
            )
        return None

    def parse_class2_pair_from_alpha_and_beta_strings(
        self, alpha, beta, default_species=None, require_alleles=False
    ):
        """
        If a name is known to contain "/" then it's
        expected to be of a format like:
            HLA-DQA*01:01/DQB*01:02

        The species information from the first allele
        is used to guide parsing for the second allele.
        """
        alpha_result = self.parse(
            alpha, infer_class2_pairing=False, default_species=default_species, raise_on_error=False
        )

        if alpha_result is None:
            return None

        if type(alpha_result) not in (Allele, Gene):
            return None

        if require_alleles and type(alpha_result) is not Allele:
            return None

        species_for_beta = alpha_result.species
        if species_for_beta is None:
            species_for_beta = default_species

        beta_result = self.parse(
            beta, default_species=species_for_beta, infer_class2_pairing=False, raise_on_error=False
        )
        if beta_result is None or (require_alleles and type(beta_result) is not Allele):
            return None
        if alpha_result.species != beta_result.species:
            return None
        return Pair.get(alpha_result, beta_result)

    def parse_mutations(self, species, mutation_strings):
        """
        Returns two dictionaries:
            chain_to_mutations
            gene_to_mutations

        When no gene or chain is selected, mutations are added to the
        chain_to_mutations dictionary under the key "no_chain".
        """
        # expect names with spaces to be like "A*02:07 T80M mutant"
        # trim off final commas in case we encounter a list of
        # mutations like: "E152A, R155Y, L156Y mutant"
        mutations_without_selector = []
        chain_to_mutations = defaultdict(list)
        gene_to_mutations = defaultdict(list)
        # assume mutations apply to beta chain of Class II but if the
        # underlying allele ends up being a Class I MHC then
        # just give it all the parsed mutations
        selected_chain = None
        for mutation_string in mutation_strings:
            mutation_string = mutation_string.strip().lower()
            if not mutation_string:
                continue
            if mutation_string.endswith(","):
                mutation_string = mutation_string[:-1]

            if mutation_string in {"alpha", "beta"}:
                selected_chain = mutation_string
                continue
            elif ":" in mutation_string:
                # if the mutation is selecting out the gene it's mutating,
                # have to parse that separately
                if mutation_string.count(":") != 1:
                    return None
                gene_selector, mutation_string = mutation_string.split(":")
                gene = Gene.get(species, gene_selector)
                if not gene:
                    return None
            else:
                gene = None
            mut = Mutation.parse(mutation_string, raise_on_error=False)
            if mut is None:
                return None
            if gene:
                gene_to_mutations[gene].append(mut)
            elif selected_chain:
                chain_to_mutations[selected_chain].append(mut)
            else:
                mutations_without_selector.append(mut)
        return mutations_without_selector, chain_to_mutations, gene_to_mutations

    def apply_mutations(
        self,
        result_without_mutation,
        mutations_without_selector,
        chain_to_mutations,
        gene_to_mutations,
    ):
        n_mutations = (
            len(mutations_without_selector) + len(gene_to_mutations) + len(chain_to_mutations)
        )

        if not n_mutations:
            return None

        result = result_without_mutation

        alpha_mutations = chain_to_mutations["alpha"]
        beta_mutations = chain_to_mutations["beta"]

        if type(result) in (Gene, Allele):
            mutations = list(mutations_without_selector)

            for gene, mutations_for_gene in gene_to_mutations.items():
                if gene != result_without_mutation.gene:
                    return None
                mutations.extend(mutations_for_gene)

            if result.is_class2_alpha:
                if beta_mutations:
                    return None
                mutations.extend(alpha_mutations)
            elif result.is_class2_beta:
                mutations.extend(beta_mutations)
            else:
                if alpha_mutations or beta_mutations:
                    return None
            result = result.copy_with_extra_mutations(mutations)
        elif type(result) is Pair:
            beta_mutations.extend(mutations_without_selector)
            alpha, beta = result.alpha, result.beta
            for gene, mutations_for_gene in gene_to_mutations.items():
                if gene == alpha.gene:
                    alpha_mutations.extend(mutations_for_gene)
                elif gene == beta.gene:
                    beta_mutations.extend(mutations_for_gene)
                else:
                    # unexpected gene!
                    return None
            alpha = alpha.copy_with_extra_mutations(alpha_mutations)
            beta = beta.copy_with_extra_mutations(beta_mutations)
            result = result.copy(alpha=alpha, beta=beta)
        else:
            return None
        return result

    def parse_and_apply_mutations(
        self, result_without_mutation: Union[Gene, Allele, Pair], mutation_tokens: Sequence[Token]
    ) -> Union[Gene, Allele, Pair, None]:
        """
        Parameters
        ----------
        result_without_mutation : Result

        mutation_strings : list[str]

        default_species : str or None

        Returns Gene, Allele, or Pair
        """
        if type(result_without_mutation) in (Serotype, Haplotype):
            result_without_mutation = result_without_mutation.collapse_if_possible()

        if result_without_mutation is None:
            return None

        if type(result_without_mutation) not in (Gene, Allele, Pair):
            return None

        if len(mutation_tokens) == 0:
            return None

        while mutation_tokens and mutation_tokens[-1].is_mutant:
            mutation_tokens = mutation_tokens[:-1]

        if len(mutation_tokens) == 0:
            return None

        mutation_strings = [tok.seq for tok in mutation_tokens]

        parse_result = self.parse_mutations(
            species=result_without_mutation.species, mutation_strings=mutation_strings
        )

        if parse_result is None:
            return None

        mutations_without_selector, chain_to_mutations, gene_to_mutations = parse_result

        return self.apply_mutations(
            result_without_mutation,
            mutations_without_selector,
            chain_to_mutations,
            gene_to_mutations,
        )

    def adjust_raw_strings(self, candidates: Sequence[Result], raw_string: str):
        """
        Annotate every ParseResult in a list with its `raw_string` field
        updated to `raw_string`.

        Returns
        -------
        List of Result objects
        """
        results = []
        for parse_candidate in candidates:
            if parse_candidate.raw_string != raw_string:
                parse_candidate = parse_candidate.copy(raw_string=raw_string)
            assert parse_candidate is not None
            results.append(parse_candidate)
        return results

    def transform_parse_candidate(self, parse_candidate: Result):
        """
        Perform optional transformations on Result objects such as collapsing
        singleton serotypes and haplotypes.
        """
        if parse_candidate is None:
            return None
        # if parse_candidate in self._transform_cache: ##FG removed. causing caching issues
        #     return self._transform_cache[parse_candidate]
        t = type(parse_candidate)
        transformed = None
        if t in (Serotype, Haplotype):
            old_alleles = parse_candidate.alleles
            new_alleles = self.transform_parse_candidates(old_alleles)
            if old_alleles != new_alleles:
                transformed = parse_candidate.copy(alleles=new_alleles)
            if (self.collapse_singleton_haplotypes and t is Haplotype) or (
                self.collapse_singleton_serotypes and t is Serotype
            ):
                if transformed is None:
                    transformed = parse_candidate.collapse_if_possible()
                else:
                    transformed = transformed.collapse_if_possible()
        elif t is Pair:
            alpha = self.transform_parse_candidate(parse_candidate.alpha)
            beta = self.transform_parse_candidate(parse_candidate.beta)
            if alpha != parse_candidate.alpha or beta != parse_candidate.beta:
                if (
                    isinstance(alpha, AlleleWithoutGene)
                    and isinstance(beta, AlleleWithoutGene)
                    and alpha.species == beta.species
                ):
                    # A slash between two gene-less allele designators of the
                    # same species is IPD-style typing ambiguity (e.g.
                    # SahaI*74/88), not a class II alpha/beta pair. The right
                    # side of the slash is tokenized as a bare number and
                    # lacks class context on its own, so propagate the class
                    # from whichever member resolved it.
                    shared_class = alpha.mhc_class or beta.mhc_class
                    if shared_class is not None:
                        if alpha.mhc_class is None:
                            alpha = AlleleWithoutGene.get(
                                alpha.species,
                                alpha.name,
                                mhc_class=shared_class,
                                raw_string=alpha.raw_string,
                            )
                        if beta.mhc_class is None:
                            beta = AlleleWithoutGene.get(
                                beta.species,
                                beta.name,
                                mhc_class=shared_class,
                                raw_string=beta.raw_string,
                            )
                    transformed = AmbiguousAlleles(
                        species=alpha.species,
                        alleles=(alpha, beta),
                        raw_string=parse_candidate.raw_string,
                    )
                else:
                    transformed = Pair.get(alpha, beta, raw_string=parse_candidate.raw_string)
        elif t in (AlleleWithoutGene, Allele):
            raw_string = parse_candidate.raw_string
            species = parse_candidate.species
            if t is Allele:
                gene = parse_candidate.gene
                gene_name = gene.name
                # Preserve class context when alias resolution strips the
                # source gene — e.g. Saha's "I" placeholder gene carries
                # mhc_class='I' and the resulting AlleleWithoutGene should
                # remain discoverable via is_class1 / mhc_class filters.
                source_mhc_class = gene.mhc_class
            else:
                gene = gene_name = None
                source_mhc_class = parse_candidate.mhc_class
            old_name = parse_candidate.name
            transformed = None
            if self.use_allele_aliases:
                allele_alias = species.get_allele_alias(gene_name=gene_name, allele_name=old_name)

                if allele_alias is not None:
                    new_gene_name, new_allele_name = allele_alias
                    if new_gene_name is None:
                        if "*" not in new_allele_name:
                            transformed = AlleleWithoutGene.get(
                                species,
                                new_allele_name,
                                mhc_class=source_mhc_class,
                                raw_string=raw_string,
                            )
                    else:
                        if new_gene_name == gene_name:
                            new_gene = gene
                        else:
                            new_gene = Gene.get(species, new_gene_name)
                        if new_gene is not None:
                            transformed = self.parse_allele_with_gene(
                                new_gene, new_allele_name, preserve_caps=True, raw_string=raw_string
                            )

            if transformed is None:
                known_allele = species.get_known_allele(gene_name=gene_name, allele_name=old_name)
                if known_allele is not None:
                    new_gene_name, new_allele_name = known_allele
                    if new_gene_name is None:
                        if "*" not in new_allele_name:
                            transformed = AlleleWithoutGene.get(
                                species,
                                new_allele_name,
                                mhc_class=source_mhc_class,
                                raw_string=raw_string,
                            )
                    else:
                        if new_gene_name == gene_name:
                            new_gene = gene
                        else:
                            new_gene = Gene.get(species, new_gene_name)
                        if new_gene is not None:
                            transformed = self.parse_allele_with_gene(
                                new_gene, new_allele_name, preserve_caps=True, raw_string=raw_string
                            )
        if self.verbose:
            print("=== Transform ===")
            print(f"In:  {parse_candidate}")
            print(f"Out: {transformed}")
        if transformed is not None:
            result = transformed
        else:
            result = parse_candidate
        self._transform_cache[parse_candidate] = result
        return result

    def transform_parse_candidates(self, parse_candidates: Sequence[Result]):
        """
        Apply transform_parse_candidate to a list of results.
        """
        results = []
        for parse_candidate in parse_candidates:
            result = self.transform_parse_candidate(parse_candidate)
            if result:
                results.append(result)
        results = unique(results)

        # Preserve established chicken haplotype behavior such as BF19. If a
        # haplotype name exactly matches another candidate's compact form, the
        # haplotype should win instead of surfacing an additional generic
        # family-level allele candidate.
        haplotype_names = {
            result.name.lower()
            for result in results
            if isinstance(result, Haplotype) and result.name is not None
        }
        if haplotype_names:
            filtered_results = []
            for result in results:
                if isinstance(result, Haplotype):
                    filtered_results.append(result)
                    continue
                if not isinstance(result, Allele):
                    filtered_results.append(result)
                    continue
                try:
                    compact_name = result.compact_string(with_species=False).lower()
                except TypeError:
                    compact_name = result.compact_string().lower()
                if compact_name not in haplotype_names:
                    filtered_results.append(result)
            results = filtered_results

        return results

    def parse_gene_without_species(
        self,
        gene_name: str,
        default_species: Union[Sequence, str, None] = None,
        strict_default_species: bool = False,
    ):
        """
        Parse the gene name without any associated species based on being
        either a unique gene name across all species or matching the default
        species.

        Returns Species or None
        """
        if strict_default_species and default_species is not None:
            return Gene.get(default_species, gene_name)

        species = None
        species_candidates = Species.get_species_with_gene_name(gene_name)
        if (
            len(species_candidates) > 1
            and default_species is not None
            and default_species in species_candidates
        ):
            species = default_species
        if len(species_candidates) == 1:
            species = species_candidates[0]
        # When a distinctive gene name (contains a digit, e.g. BF2, DPB1)
        # is shared by multiple species, pick the best-characterised one.  This
        # avoids breaking bare "BF2" -> chicken when guineafowl also
        # carries BF2.  We skip single-letter genes like "A" or "E"
        # because they are too generic and the ambiguity should fall
        # through to other parse strategies.
        #
        # A gene defined on a broad parent group is visible to every species
        # beneath it, so most of these candidates never use the name at all.
        # Rank the ones whose own ontology entry declares the gene above the
        # ones that merely inherit it, and only then fall back to how many
        # genes a species has.  Bare "BLB2" used to resolve to Coturnix
        # japonica, which inherits BLB1/BLB2 from "Galliformes sp." and calls
        # its own class II beta genes DAB1/DBB1/DCB1, over Gallus gallus,
        # which declares them.
        #
        # Gene lookup is case-normalizing, so distinct genes can collide:
        # "Ia1" belongs to Paralichthys olivaceus and "IA1" to Chrysolophus
        # pictus.  Prefer the species that spells the gene the way the caller
        # did before falling back to a case-insensitive match.
        if species is None and len(species_candidates) > 1 and any(c.isdigit() for c in gene_name):
            species = max(
                species_candidates,
                key=lambda s: (
                    s.declares_gene_with_same_case(gene_name),
                    s.declares_gene(gene_name),
                    s.num_genes,
                    # purely so a genuine tie resolves the same way every run;
                    # a later latin name is not a better answer
                    s.name,
                ),
            )
        if species is None:
            return None
        return Gene.get(species, gene_name)

    def parse_allele_without_species(
        self,
        allele_name: str,
        default_species: Union[str, Species, None] = None,
        strict_default_species: bool = False,
    ):
        """
        Parse the allele name without any associated species based on being
        having a unique gene name across all species or matching the default
        species.

        Returns Species or None
        """
        if not allele_name:
            return None
        if allele_name.count("*") == 1:
            gene_name, allele_string = allele_name.split("*")
        else:
            gene_name, allele_string = split_digits_at_end(allele_name)

        if gene_name and allele_string:
            gene = self.parse_gene_without_species(
                gene_name=gene_name,
                default_species=default_species,
                strict_default_species=strict_default_species,
            )
            if gene:
                return self.parse_allele_or_gene_candidates(
                    species=gene.species, str_after_species=allele_name, raw_string=allele_name
                )
        return None

    def parse_class_marker_after_species(self, species, str_after_species):
        """
        The hyphenated class shorthand: "SLA-I", "BoLA-II", "HLA-I".

        Common in the literature, and it returned None for almost every species
        before 3.47.0 -- so a caller pulling MHC tokens out of curated text got
        nothing at all and the sample silently ended up with no genotype (#104).

        Offered as one candidate among the others rather than short-circuiting,
        because two species have a better answer: Mamu-I is a published macaque
        class I locus (J Immunol 2000;164:1386, "Mamu-I: A Novel Primate MHC
        Class I B-Related Locus") and H2-i is a mouse haplotype. Result sorting
        decides between them.

        Roman numerals only. "SLA-1", "BoLA-1" and "ELA-1" are real class I
        gene names, so mapping the digits would shadow genuine loci for some
        species and not others -- recreating the inconsistency this fixes.
        """
        normalized = str_after_species.strip().strip("-").lower()
        if normalized == "i":
            return MhcClass.get(species, "I")
        if normalized == "ii":
            return MhcClass.get(species, "II")
        return None

    def parse_single_token_to_multiple_candidates(
        self,
        token: Token,
        default_species: Union[str, Species, None] = DEFAULT_SPECIES_PREFIX,
        strict_default_species: bool = False,
    ):
        """
        Returns list of result objects for a single token string which
        should not contain any whitespace.
        """
        if self.verbose:
            print(f""">>> Parser.parse_single_token_to_multiple_candidates(
                            {token}, {default_species})""")

        # if the whole sequence is just something like "Class I" then return that
        # result directly
        if token.is_class1_or_class2:
            mhc_class = MhcClass.get(default_species, "I" if token.is_class1 else "II")
            if mhc_class:
                return [mhc_class]

        # MHC class + chain labels: MHCIIB, MHCIIA, MHCIA, MHC-IIB, mhc2b, mhc1, etc.
        # These are region labels meaning "class N [alpha/beta], unknown locus"
        # rather than specific gene names. Return MhcClass with optional chain= set.
        mhc_region = _parse_mhc_region_label(token.seq)
        if mhc_region is not None:
            mhc_class_str, chain = mhc_region
            result = MhcClass.get(default_species, mhc_class_str, chain=chain)
            if result:
                return [result]

        seq = token.seq
        raw_string = token.raw_string

        standard_result = parse_standard_allele_format(
            seq, raw_string=raw_string, default_species=default_species
        )

        if standard_result:
            if self.verbose:
                print("""=== Standard format result """)
                print(standard_result)
            return [standard_result]

        explicit_species, str_after_explicit_species = self.parse_species_from_prefix(name=seq)
        if explicit_species is not None:
            if (
                strict_default_species
                and default_species is not None
                and explicit_species != Species.get(default_species)
            ):
                return []
            parse_candidates = []
            str_after_explicit_species = self.strip_extra_chars(str_after_explicit_species)
            if len(str_after_explicit_species) == 0:
                parse_candidates.append(explicit_species)
            else:
                if self.verbose:
                    print("=== Functions with explicit species prefix ===")
                fns_with_species = [
                    Class2Locus.get,
                    Gene.get,
                    self.parse_class_marker_after_species,
                    self.get_heterodimer,
                    self.get_serotype,
                    self.get_supertype,
                    self.get_haplotype,
                    self.parse_allele_or_gene_candidates,
                    self.parse_class2_pair_with_hyphen_sep,
                    self.parse_haplotype_with_class2_locus_from_any_string_split,
                ]
                for fn in fns_with_species:
                    result = fn(explicit_species, str_after_explicit_species)
                    if self.verbose:
                        print(
                            "{}({}, '{}') = {}".format(
                                fn.__qualname__,
                                explicit_species,
                                seq,
                                "None" if not result else f"{result}",
                            )
                        )
                    if result is None:
                        continue
                    if type(result) in (list, tuple):
                        parse_candidates.extend(result)
                    elif isinstance(result, Result):
                        parse_candidates.append(result)
                    else:
                        raise ParseError(
                            f"Unexpected result '{result}' while parsing '{raw_string}'"
                        )
                full_token_haplotype = self.parse_haplotype(
                    seq, default_species=explicit_species, strict_default_species=True
                )
                if (
                    full_token_haplotype is not None
                    and full_token_haplotype.has_species
                    and full_token_haplotype.species == explicit_species
                ):
                    parse_candidates.append(full_token_haplotype)
            parse_candidates = unique(parse_candidates)
            return self.adjust_raw_strings(parse_candidates, raw_string=raw_string)

        # list containing all candidate results
        parse_candidates = []

        # all of these functions are expected to take the sequence
        # without any additional knowledge of which species it is associated
        # with.
        fns_without_species = [
            self.parse_haplotype,
            self.parse_gene_without_species,
            self.parse_allele_without_species,
        ]
        if self.verbose:
            print("=== Functions without required species argument ===")
        for fn in fns_without_species:
            result = fn(
                seq,
                default_species=default_species,
                strict_default_species=strict_default_species,
            )

            if self.verbose:
                print(
                    "{}('{}', default_species={}) = {}".format(
                        fn.__qualname__,
                        seq,
                        (f"{default_species}" if type(default_species) is str else default_species),
                        (f"{result}" if type(result) is str else result),
                    )
                )
            if result is None:
                continue
            if type(result) in (list, tuple):
                parse_candidates.extend(result)
            elif isinstance(result, Result):
                parse_candidates.append(result)

        species, str_after_species = self.parse_species(name=seq, default_species=default_species)

        # When nothing in the token named a species, parse_species hands back
        # the default species and the whole token as the remainder. A gene
        # marked `context only` must not be resolved on that assumption: bare
        # "N" is rat haplotype shorthand, and only "HLA-N" or an explicit
        # species= argument makes it the human class I fragment. See #113.
        species_was_named = strict_default_species or str_after_species != seq

        if species is not None:
            if len(str_after_species) == 0:
                parse_candidates.append(species)
            else:
                if self.verbose:
                    print("=== Functions with required species argument ===")
                # all of these functions are expected to take two arguments
                # (Species, str_after_species) and returns either a parsed
                # represntation or None
                fns_with_species = [
                    Class2Locus.get,
                    Gene.get,
                    self.parse_class_marker_after_species,
                    self.get_heterodimer,  # Check heterodimers before serotypes (DQ2.5 vs DQ2)
                    self.get_serotype,
                    self.get_supertype,  # Check supertypes (A02, B07, etc.)
                    self.get_haplotype,
                    self.parse_allele_or_gene_candidates,
                    self.parse_class2_pair_with_hyphen_sep,
                    self.parse_haplotype_with_class2_locus_from_any_string_split,
                ]

                for fn in fns_with_species:
                    result = fn(species, str_after_species)
                    if self.verbose:
                        print(
                            "{}({}, '{}') = {}".format(
                                fn.__qualname__, species, seq, "None" if not result else f"{result}"
                            )
                        )
                    if result is None:
                        continue
                    if type(result) in (list, tuple):
                        parse_candidates.extend(result)
                    elif isinstance(result, Result):
                        parse_candidates.append(result)
                    else:
                        raise ParseError(
                            f"Unexpected result '{result}' while parsing '{raw_string}'"
                        )
                if not species_was_named:
                    parse_candidates = [
                        candidate
                        for candidate in parse_candidates
                        if not _names_context_only_gene(candidate)
                    ]
        parse_candidates = unique(parse_candidates)
        # update all the objects to set their raw_string field to raw_string
        # and also perform optional transformations
        return self.adjust_raw_strings(parse_candidates, raw_string=raw_string)

    def restrict_result_type_if_possible(
        self, results: Sequence[Result], preferred_types: Sequence[type]
    ):
        """
        Filter results to any of given types, as long as some results remain.
        Otherwise return all results.
        """
        if type(preferred_types) not in (list, set, tuple):
            preferred_types = [preferred_types]
        if type(preferred_types) is not tuple:
            preferred_types = tuple(preferred_types)
        filtered_results = [result for result in results if isinstance(result, preferred_types)]
        if filtered_results:
            return filtered_results
        else:
            return results

    def parse_with_class_token_to_multiple_candidates(
        self,
        class_token: Token,
        other_tokens: Sequence[Token],
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        strict_default_species: bool = False,
    ):
        class1 = class_token.is_class1
        class2 = class_token.is_class2
        mhc_class_string = "I" if class1 else "II"

        candidates = []
        if len(other_tokens) == 0:
            mhc_class = MhcClass.get(default_species, mhc_class_string)
            if mhc_class:
                candidates.append(mhc_class)
        else:
            for unrestricted_result in self.parse_tokens_to_multiple_candidates(
                tokens=other_tokens,
                default_species=default_species,
                strict_default_species=strict_default_species,
            ):
                t = type(unrestricted_result)
                if t is Haplotype:
                    restricted = unrestricted_result.restrict_mhc_class(mhc_class_string)
                    if restricted:
                        candidates.append(restricted)
                elif t is Species:
                    mhc_class = MhcClass.get(unrestricted_result, mhc_class_string)
                    if mhc_class:
                        candidates.append(mhc_class)
                elif unrestricted_result.has_mhc_class:
                    if (class1 and unrestricted_result.is_class1) or (
                        class2 and unrestricted_result.is_class2
                    ):
                        candidates.append(unrestricted_result)
        return unique(candidates)

    def parse_with_haplotype_token_to_multiple_candidates(
        self,
        maybe_species_token: Token,
        other_tokens: Sequence[Token],
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        strict_default_species: bool = False,
    ):
        """
        Parse "Haplotype H2 L-q" but also "Haplotype H2-k"
        Or: "L-q H2 Haplotype"
        Returns list of results
        """
        # First try parsing the second token as a species:
        species = Species.get(maybe_species_token)
        if not species:
            return self.restrict_result_type_if_possible(
                results=self.parse_tokens_to_multiple_candidates(
                    tokens=(maybe_species_token, *other_tokens),
                    default_species=default_species,
                    strict_default_species=strict_default_species,
                ),
                preferred_types=[Haplotype],
            )

        if not other_tokens:
            # sequences like "haplotype H2" just map to the species
            return [species]

        return self.parse_tokens_to_multiple_candidates(
            tokens=other_tokens, default_species=species, strict_default_species=True
        )

    def parse_tokens_around_slash(
        self,
        tokens_before: Sequence[Token],
        tokens_after: Sequence[Token],
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        strict_default_species: bool = False,
    ):
        if len(tokens_before) == 0:
            return self.parse_tokens_to_multiple_candidates(
                tokens=tokens_after,
                default_species=default_species,
                strict_default_species=strict_default_species,
            )
        elif len(tokens_after) == 0:
            return self.parse_tokens_to_multiple_candidates(
                tokens=tokens_before,
                default_species=default_species,
                strict_default_species=strict_default_species,
            )
        candidates = []
        for result_before in self.parse_tokens_to_multiple_candidates(
            tokens=tokens_before,
            default_species=default_species,
            strict_default_species=strict_default_species,
        ):
            if result_before is None:
                continue
            if type(result_before) is Haplotype:
                if len(tokens_after) not in {1, 2}:
                    continue
                if tokens_after[0].can_be_identifier:
                    haplotype = self.create_crossed_haplotype(
                        first_haplotype_object=result_before,
                        second_haplotype_name=tokens_after[0].seq,
                    )
                    if haplotype is None:
                        continue
                    elif len(tokens_after) == 1:
                        candidates.append(haplotype)
                    elif len(tokens_after) == 2 and tokens_after[1].is_class1_or_class2:
                        class1 = tokens_after[1].is_class1
                        restricted_haplotype = haplotype.restrict_mhc_class(
                            class_restriction="I" if class1 else "II"
                        )
                        if restricted_haplotype:
                            candidates.append(restricted_haplotype)
            elif type(result_before) in (Allele, Gene):
                if result_before.has_species:
                    species = result_before.species
                else:
                    species = default_species
                for result_after in self.parse_tokens_to_multiple_candidates(
                    tokens=tokens_after,
                    default_species=species,
                    strict_default_species=True,
                ):
                    if result_after is None:
                        continue
                    if not hasattr(result_after, "species"):
                        continue
                    if result_before.species != result_after.species:
                        continue
                    class2_pair = Pair.get(result_before, result_after)
                    if class2_pair:
                        candidates.append(class2_pair)
            elif type(result_before) is AlleleWithoutGene:
                # IPD-style slash ambiguity between two gene-less allele
                # designators of the same species, e.g. "SahaI*74/88" from
                # Caldwell et al. 2018 (PMC6092122) which cannot be
                # attributed to SahaI*74 or SahaI*88 from the typed region.
                species = result_before.species if result_before.has_species else default_species
                for result_after in self.parse_tokens_to_multiple_candidates(
                    tokens=tokens_after,
                    default_species=species,
                    strict_default_species=True,
                ):
                    if not isinstance(result_after, AlleleWithoutGene):
                        continue
                    if result_before.species != result_after.species:
                        continue
                    candidates.append(
                        AmbiguousAlleles(
                            species=result_before.species,
                            alleles=(result_before, result_after),
                        )
                    )
        return unique(candidates)

    def resolve_class2_locus_chain_gene(self, locus: Class2Locus, chain: str):
        if chain == "alpha":
            chain_genes = locus.alpha_chain_genes
            chain_letter = "A"
        elif chain == "beta":
            chain_genes = locus.beta_chain_genes
            chain_letter = "B"
        else:
            raise ValueError(f"Unexpected chain: {chain}")

        if len(chain_genes) == 1:
            return chain_genes[0]

        valid_gene_names = {gene.name for gene in chain_genes}
        candidate_gene_tokens = (
            f"{locus.name}-{chain}",
            f"{locus.name}{chain_letter}",
            f"{locus.name}{chain_letter.lower()}",
        )
        for candidate_gene_token in candidate_gene_tokens:
            canonical_gene_name = locus.species.find_matching_gene_name(candidate_gene_token)
            if canonical_gene_name is None:
                continue
            if canonical_gene_name not in valid_gene_names:
                continue
            return Gene.get(locus.species, canonical_gene_name)
        return None

    def parse_tokens_to_multiple_candidates(
        self,
        tokens: Sequence[Token],
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        strict_default_species: bool = False,
    ):
        if len(tokens) == 0:
            return []
        elif len(tokens) == 1:
            # no whitespace, so nothing else in this function applies
            return self.parse_single_token_to_multiple_candidates(
                token=tokens[0],
                default_species=default_species,
                strict_default_species=strict_default_species,
            )
        elif "/" in tokens:
            slash_index = tokens.index("/")
            return self.parse_tokens_around_slash(
                tokens_before=tokens[:slash_index],
                tokens_after=tokens[slash_index + 1 :],
                default_species=default_species,
                strict_default_species=strict_default_species,
            )

        # if the token sequence didn't start with a recognizable species name
        # then continue here
        candidates = []
        if tokens[-1].is_alpha:
            for candidate in self.parse_tokens_to_multiple_candidates(
                tokens=tokens[:-1],
                default_species=default_species,
                strict_default_species=strict_default_species,
            ):
                if type(candidate) in (Allele, AlleleWithoutGene, Gene):
                    if candidate.is_class1 or candidate.is_class2_alpha:
                        candidates.append(candidate)
                elif type(candidate) is Pair:
                    candidates.append(candidate.alpha)
                elif type(candidate) is Class2Locus:
                    alpha_gene = self.resolve_class2_locus_chain_gene(candidate, chain="alpha")
                    if alpha_gene is not None:
                        candidates.append(alpha_gene)
                elif type(candidate) is MhcClass:
                    candidates.append(candidate.copy(chain="alpha"))
            if not candidates:
                # Fallback: try joining preceding token(s) with "-alpha" as a
                # compound gene name, e.g., ["i-e", alpha] → "i-e-alpha" which
                # can match gene aliases like IE-alpha → EA across species.
                combined = "-".join(t.seq for t in tokens[:-1]) + "-alpha"
                combined_token = Token(
                    seq=combined,
                    raw_string=" ".join(t.raw_string for t in tokens),
                )
                candidates.extend(
                    self.parse_single_token_to_multiple_candidates(
                        token=combined_token,
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    )
                )
        elif tokens[-1].is_beta:
            for candidate in self.parse_tokens_to_multiple_candidates(
                tokens=tokens[:-1],
                default_species=default_species,
                strict_default_species=strict_default_species,
            ):
                if type(candidate) in (Allele, AlleleWithoutGene, Gene):
                    if candidate.is_class2_beta:
                        candidates.append(candidate)
                elif type(candidate) is Pair:
                    candidates.append(candidate.beta)
                elif type(candidate) is Class2Locus:
                    beta_gene = self.resolve_class2_locus_chain_gene(candidate, chain="beta")
                    if beta_gene is not None:
                        candidates.append(beta_gene)
                elif type(candidate) is MhcClass:
                    candidates.append(candidate.copy(chain="beta"))
            if not candidates:
                # Fallback: try joining preceding token(s) with "-beta" as a
                # compound gene name, e.g., ["i-e", beta] → "i-e-beta" which
                # can match gene aliases like IE-beta → EB across species.
                combined = "-".join(t.seq for t in tokens[:-1]) + "-beta"
                combined_token = Token(
                    seq=combined,
                    raw_string=" ".join(t.raw_string for t in tokens),
                )
                candidates.extend(
                    self.parse_single_token_to_multiple_candidates(
                        token=combined_token,
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    )
                )
        elif tokens[-1].is_mutant:
            for without_mutation in self.parse_single_token_to_multiple_candidates(
                token=tokens[0],
                default_species=default_species,
                strict_default_species=strict_default_species,
            ):
                if not without_mutation:
                    continue
                with_mutation = self.parse_and_apply_mutations(
                    result_without_mutation=without_mutation, mutation_tokens=tokens[1:-1]
                )
                if with_mutation is None:
                    continue
                candidates.append(with_mutation)

        elif tokens[-1].is_class1_or_class2:
            # Parse MHC classes, haplotypes, or serotypes such as:
            # - "HLA class I" => tokenized as ("hla", "class-1")
            # - "ELA-A1 class I" => tokenized as ("ela-a1", "class-1")
            candidates.extend(
                self.parse_with_class_token_to_multiple_candidates(
                    class_token=tokens[-1],
                    other_tokens=tokens[:-1],
                    default_species=default_species,
                    strict_default_species=strict_default_species,
                )
            )
        elif tokens[0].is_class1_or_class2:
            # Parse MHC classes, haplotypes, or serotypes such as:
            # - "class I HLA" => tokenized as ("class-1", "hla)
            # - "Class I H2-b " => tokenized as ("class-1", "h2-b")
            candidates.extend(
                self.parse_with_class_token_to_multiple_candidates(
                    class_token=tokens[0],
                    other_tokens=tokens[1:],
                    default_species=default_species,
                    strict_default_species=strict_default_species,
                )
            )

        elif len(tokens) >= 3 and tokens[1].is_class1_or_class2:
            # parse strings like "MOUSE MHC class I L-q" as an allele
            # Tokenization normalizes this sequence into:
            #   ("mouse", "class-1", "L-q")

            species = Species.get(tokens[0].seq)

            if species:
                class1 = tokens[1].is_class1
                class2 = tokens[1].is_class2
                for candidate in self.parse_tokens_to_multiple_candidates(
                    tokens=tokens[2:], default_species=species, strict_default_species=True
                ):
                    if (class1 and candidate.is_class1) or (class2 and candidate.is_class2):
                        candidates.append(candidate)

        elif tokens[0].is_haplotype:
            # parse one of the following formats:
            #   - "haplotype H2 L-q " (here haplotype just means species)
            #   - "haplotype H2-k" (unrestricted haplotype)
            #   - "haplotype H2-k class I" (restricted haplotype)
            candidates.extend(
                self.parse_with_haplotype_token_to_multiple_candidates(
                    maybe_species_token=tokens[1],
                    other_tokens=tokens[2:],
                    default_species=default_species,
                    strict_default_species=strict_default_species,
                )
            )

        elif tokens[-1].is_haplotype:
            # parse "L-q H2 haplotype" but also "H2-k haplotype"
            candidates.extend(
                self.parse_with_haplotype_token_to_multiple_candidates(
                    maybe_species_token=tokens[-2],
                    other_tokens=tokens[:-2],
                    default_species=default_species,
                    strict_default_species=strict_default_species,
                )
            )
        elif tokens[-1].is_gene:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[:-1],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Gene],
                )
            )
        elif tokens[0].is_gene:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[1:],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Gene],
                )
            )
        elif tokens[-1].is_allele:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[:-1],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Allele],
                )
            )
        elif tokens[0].is_allele:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[1:],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Allele],
                )
            )
        elif tokens[-1].is_serotype:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[:-1],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Serotype],
                )
            )
        elif tokens[0].is_serotype:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[1:],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Serotype],
                )
            )
        elif tokens[-1].is_supertype:
            # Handle "A2 supertype", "HLA A2 supertype", etc.
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[:-1],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Supertype],
                )
            )
        elif tokens[0].is_supertype:
            # Handle "supertype A2", "supertype B7", etc.
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[1:],
                        default_species=default_species,
                        strict_default_species=strict_default_species,
                    ),
                    preferred_types=[Supertype],
                )
            )
        elif len(tokens) == 2:
            first_token, second_token = tokens
            for first_result in self.parse_single_token_to_multiple_candidates(
                token=first_token,
                default_species=default_species,
                strict_default_species=strict_default_species,
            ):
                if type(first_result) is Species:
                    if (
                        strict_default_species
                        and default_species is not None
                        and first_result != Species.get(default_species)
                    ):
                        continue
                    for second_result in self.parse_single_token_to_multiple_candidates(
                        token=second_token,
                        default_species=first_result,
                        strict_default_species=True,
                    ):
                        if (
                            isinstance(second_result, ResultWithSpecies)
                            and second_result.species == first_result
                        ):
                            candidates.append(second_result)
        return self.transform_parse_candidates(candidates)

    def select_species_from_optional_attributes(self, attributes: Mapping[str, str]):
        """
        If input sequence had attributes like 'OS=Mus musculus' then use those
        to select the default species.
        """
        if "OS" in attributes:
            return Species.get(attributes["OS"])
        elif "species" in attributes:
            return Species.get(attributes["species"])
        else:
            return None

    def parse_multiple_candidates(
        self, name: str, default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX
    ):
        """
        Returns list of ParseResult objects which are candidate interpretations
        of the given string.
        """
        tokenization_result = tokenize(name)
        trimmed_string = tokenization_result.trimmed_string
        if len(trimmed_string) == 0:
            return []

        # An MHC name has to carry at least one letter or digit. Without this
        # guard a punctuation-only string tokenizes to empty or punctuation-only
        # tokens, matches no species prefix, and falls through to the default
        # species, so "-", ".", "*" and "--" all parsed as Homo sapiens.
        if not any(c.isalnum() for c in trimmed_string):
            return []

        # "n/a" is one of the most common ways a curator or an exported
        # spreadsheet writes "missing", but it splits into the tokens
        # ("n", "/", "a"), which look exactly like a haplotype pair, so it used
        # to parse as the rat haplotype RT1-n/A. Every other null marker we
        # know of ("na", "nd", "none", "unknown", ...) already fails to match.
        if trimmed_string.strip().lower() in NULL_VALUE_STRINGS:
            return []

        tokens = tokenization_result.tokens
        if (
            len(tokens) >= 1
            and "mhc" in tokenization_result.ignored_tokens
            and tokens[0].seq.lower() in {"i", "ii", "1", "2"}
        ):
            class_token = Token(
                seq="class-1" if tokens[0].seq.lower() in {"i", "1"} else "class-2",
                raw_string=f"MHC {tokens[0].raw_string}",
            )
            descriptive_results = self.parse_with_class_token_to_multiple_candidates(
                class_token=class_token,
                other_tokens=tokens[1:],
                default_species=default_species,
                strict_default_species=False,
            )
            if descriptive_results:
                return self.transform_parse_candidates(descriptive_results)

        species_candidates = []
        found_species_prefix = False
        for num_species_tokens in [3, 2, 1]:
            if len(tokens) >= (num_species_tokens + 1):
                # try peeling off species names such as
                # "homo sapiens" at the beginning of a token sequence
                species_query = " ".join([t.seq for t in tokens[:num_species_tokens]])
                species_candidates = find_matching_species_objects(species_query)
            if len(species_candidates) > 0:
                # A species prefix is inherited by every descendant, so a bare
                # prefix matches an ancestor and everything under it: "BoLA"
                # matches Bos sp. but also Bubalus bubalis, and "RT1" matches
                # Rattus sp. plus every Rattus species. Nothing in the input
                # named a descendant, so defer to Species.get, which walks the
                # resolution ladder (exact latin name, exact prefix owner, then
                # the non-descendant). It returns None for a genuine collision
                # between unrelated species, in which case every candidate is
                # kept and gene context decides.
                if len(species_candidates) > 1:
                    prefix_owner = Species.get(species_query)
                    if prefix_owner is not None:
                        species_candidates = [prefix_owner]
                tokens = tokens[num_species_tokens:]
                found_species_prefix = True
                break

        results = []
        if found_species_prefix:
            # if anything at the start of the token sequence matched a species
            # name then just go with those species possibilities and throw away
            # the default one we're using
            if len(tokens) == 0:
                results.extend(species_candidates)
            elif (
                "mhc" in tokenization_result.ignored_tokens
                and len(tokens) >= 2
                and tokens[0].seq.lower() in {"i", "ii", "1", "2"}
            ):
                # Handle orphaned class markers after species extraction, e.g.,
                # "mouse MHC II IE-beta" → species="mouse", tokens=["ii", "ie-beta"]
                # The "mhc" was removed during token substitution but the class
                # marker (I/II) was left behind since "class" wasn't adjacent.
                class_token = Token(
                    seq="class-1" if tokens[0].seq.lower() in {"i", "1"} else "class-2",
                    raw_string=f"MHC {tokens[0].raw_string}",
                )
                for maybe_species in species_candidates:
                    descriptive_results = self.parse_with_class_token_to_multiple_candidates(
                        class_token=class_token,
                        other_tokens=tokens[1:],
                        default_species=maybe_species,
                        strict_default_species=True,
                    )
                    results.extend(descriptive_results)
            else:
                for maybe_species in species_candidates:
                    if len(tokens) == 1 and tokens[0].is_class1:
                        mhc_class = MhcClass.get(maybe_species, "I")
                        if mhc_class is not None:
                            results.append(mhc_class)
                    elif len(tokens) == 1 and tokens[0].is_class2:
                        mhc_class = MhcClass.get(maybe_species, "II")
                        if mhc_class is not None:
                            results.append(mhc_class)
                    else:
                        maybe_results = self.parse_tokens_to_multiple_candidates(
                            tokens=tokens,
                            default_species=maybe_species,
                            strict_default_species=True,
                        )
                        # filter out the Species hits since we already have a species from
                        # the prefix
                        maybe_results = [r for r in maybe_results if type(r) is not Species]
                        results.extend(maybe_results)
        else:
            # species represented in some UniProt entries using 'OS=' attribute
            species_from_attributes = self.select_species_from_optional_attributes(
                tokenization_result.attributes
            )

            if species_from_attributes is None:
                default_species = default_species
            else:
                default_species = species_from_attributes
            results.extend(
                self.parse_tokens_to_multiple_candidates(
                    tokens=tokens,
                    default_species=default_species,
                    strict_default_species=False,
                )
            )
        if len(results) == 0 and "-" in name:
            results = self.parse_multiple_candidates(
                name.replace("-", " "), default_species=default_species
            )
            if (
                len(results) == 0
                and "GN" in tokenization_result.attributes
                and "OS" in tokenization_result.attributes
            ):
                # try just parsing the gene name
                return self.parse_multiple_candidates(
                    tokenization_result.attributes["GN"],
                    default_species=tokenization_result.attributes["OS"],
                )
        return self.transform_parse_candidates(results)

    def _parse_explicit_species_allele_candidates(self, name: str):
        """Parse a simple, explicitly species-prefixed allele without tokenizing it.

        This path reuses the complete parser's ontology-backed gene lookup,
        allele-field parsing, and candidate transformations. It deliberately
        returns no candidates for unprefixed, non-allele, or complex inputs so
        callers can fall back to the general parser.
        """
        if self.verbose or not isinstance(name, str):
            return []

        species, name_without_species = self.parse_species_from_prefix(name)
        if species is None:
            return []

        candidates = self.parse_allele_or_gene_candidates(
            species=species,
            str_after_species=self.strip_extra_chars(name_without_species),
            raw_string=name,
        )
        candidates = self.transform_parse_candidates(candidates)
        if candidates and all(
            type(candidate) is Allele
            and len(candidate.allele_fields) >= 2
            and all(field.isdigit() for field in candidate.allele_fields)
            for candidate in candidates
        ):
            return candidates
        return []

    def parse(
        self,
        name: str,
        infer_class2_pairing: bool = INFER_CLASS2_PAIRING,
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        preferred_result_types: Union[type, Iterable[type], None] = None,
        required_result_types: Union[type, Iterable[type], None] = None,
        only_class1: bool = False,
        only_class2: bool = False,
        max_allele_fields: Optional[int] = None,
        raise_on_error: bool = True,
        require_explicit_species: bool = False,
    ):
        """
        Public parse entrypoint. Returns an immutable cached result object.

        require_explicit_species : bool
            Only accept results whose species the input actually named. Use
            this when validating curated or free-text input, where a confident
            but inferred species is worse than no answer. See
            Result.species_source.
        """
        result = self._parse_cached(
            name=name,
            infer_class2_pairing=infer_class2_pairing,
            default_species=default_species,
            preferred_result_types=preferred_result_types,
            required_result_types=required_result_types,
            only_class1=only_class1,
            only_class2=only_class2,
            max_allele_fields=max_allele_fields,
            raise_on_error=raise_on_error,
        )
        if result is None:
            return None

        # Record what is needed to work out how the species was determined,
        # rather than working it out now: classification re-tokenizes the
        # string, and almost no caller asks. Result.species_source does the
        # work on first access and memoizes it. Neither field is an __init__
        # field, so equality and hashing are unaffected, and _parse_cached is
        # keyed on the input string, so a given object always carries the
        # provenance of the string it was parsed from.
        if result._species_source_inputs is None:
            Result._set_field(result, "_species_source_inputs", (name, default_species))

        if require_explicit_species and result.species_source not in (None, "explicit"):
            species_source = result.species_source
            if raise_on_error:
                raise ParseError(
                    f"Species for '{name}' was {species_source}, not explicit in the input"
                )
            return None
        return result

    @cache
    def _parse_cached(
        self,
        name: str,
        infer_class2_pairing: bool = INFER_CLASS2_PAIRING,
        default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
        preferred_result_types: Union[type, Iterable[type], None] = None,
        required_result_types: Union[type, Iterable[type], None] = None,
        only_class1: bool = False,
        only_class2: bool = False,
        max_allele_fields: Optional[int] = None,
        raise_on_error: bool = True,
    ):
        """
        Parse any MHC related string, from gene loci to fully specified 8 digit
        alleles, alpha/beta pairings of Class II MHCs, with expression modifiers
        and the description of point mutations in the molecule.

        Example of the complicated inputs this function can handle:
            HLA-DRA*01:02/DRB1*03:01 Q74R mutant
            "H2-Kb E152A, R155Y, L156Y mutant"
            SLA-1*01:01:01:01
            HLA-DRA*01:01 F54C mutant/DRB1*01:01

        Parameters
        ----------
        name : str
            Raw name of MHC locus or allele

        infer_class2_pairing : bool
            If only alpha or beta chain of Class II MHC is given, try
            to infer the missing pair?

        default_species : Species, str, or None
            Assume this species if it's not obvious in the sequence.

        preferred_result_types : list of type or None
            Prefer returning one of these result types when available.
            If none of these types match, fall back to other valid parses.

        required_result_types : list of type or None
            Strict filter. If given, only return results with types in this
            list of classes.

        only_class1 : bool
            Only return results which belong to MHC class I

        only_class2 : bool
            Only return results which belong to MHC class II

        max_allele_fields : int
            If not None, restrict number of allele fields to given value.

        raise_on_error : bool
            If False, return None when parsing is impossible.

        Returns object with one of the following types:
            - Species
            - MhcClass
            - Gene
            - Allele
            - AlleleWithoutGene
            - Pair
            - Haplotype
            - Serotype
            - Supertype
            - Class2Locus
        """
        has_candidate_filters = bool(
            preferred_result_types or required_result_types or only_class1 or only_class2
        )
        candidates = (
            [] if has_candidate_filters else self._parse_explicit_species_allele_candidates(name)
        )
        if len(candidates) == 0:
            candidates = self.parse_multiple_candidates(name, default_species=default_species)
        if len(candidates) == 0 and self.use_allele_aliases:
            resolved_alias = self._resolve_unparsed_allele_alias(name, default_species)
            if resolved_alias is not None:
                alias_species, alias_name = resolved_alias
                result = self._parse_cached(
                    name=alias_name,
                    infer_class2_pairing=infer_class2_pairing,
                    default_species=alias_species,
                    preferred_result_types=preferred_result_types,
                    required_result_types=required_result_types,
                    only_class1=only_class1,
                    only_class2=only_class2,
                    max_allele_fields=max_allele_fields,
                    raise_on_error=raise_on_error,
                )
                if result is not None and result.raw_string != name:
                    result = result.copy(raw_string=name)
                return result
        explicit_species, _ = self.parse_species_from_prefix(name)
        has_explicit_species_prefix = explicit_species is not None
        default_species_object = Species.get(default_species)
        should_require_default_match = (
            default_species is not None
            and default_species_object is not None
            and default_species_object != Species.get(DEFAULT_SPECIES_PREFIX)
        )

        # When default_species is provided, prefer candidates matching it.
        # This ensures that generic/root-level names like parse(
        # "DMA", default_species="Struthio camelus") resolve to the requested
        # species instead of a different species which also has that gene.
        if default_species is not None and len(candidates) > 0:
            ds = default_species_object
            if ds is not None:
                ds_candidates = [
                    c
                    for c in candidates
                    if (type(c) is Species and c == ds)
                    or (hasattr(c, "species") and c.species == ds)
                ]
                if ds_candidates:
                    candidates = ds_candidates
                elif should_require_default_match and not has_explicit_species_prefix:
                    if raise_on_error:
                        raise ParseError(f"Could not parse '{name}' for species '{ds.name}'")
                    return None

        if only_class1:
            candidates = [candidate for candidate in candidates if candidate.is_class1]

        if only_class2:
            candidates = [candidate for candidate in candidates if candidate.is_class2]

        if required_result_types:
            if type(required_result_types) not in (list, set, tuple):
                required_result_types = [required_result_types]
            candidates = [
                candidate for candidate in candidates if type(candidate) in required_result_types
            ]

        if preferred_result_types:
            if type(preferred_result_types) not in (list, set, tuple):
                preferred_result_types = [preferred_result_types]
            candidates_with_preferred_type = [
                candidate for candidate in candidates if type(candidate) in preferred_result_types
            ]
            if len(candidates_with_preferred_type) > 0:
                candidates = candidates_with_preferred_type

        if len(candidates) == 0:
            if raise_on_error:
                raise ParseError(f"Could not parse '{name}'")
            else:
                return None
        result = pick_best_result(candidates)

        if infer_class2_pairing:
            result = infer_class2_alpha_chain(result)

        if result.raw_string != name:
            result = result.copy(raw_string=name)

        if max_allele_fields:
            result = result.restrict_allele_fields(max_allele_fields)

        return result
