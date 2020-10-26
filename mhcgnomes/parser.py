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
from typing import Mapping, Sequence

from .allele import Allele
from .allele_annotations import (
    parse_functional_annotations_from_seq,
    parse_functional_annotations_from_allele_fields
)
from .class2_locus import Class2Locus
from .class2_pair import Class2Pair, infer_class2_alpha_chain
from .common import cache
from .data import haplotypes as raw_haplotypes_data
from .errors import ParseError
from .gene import Gene
from .haplotype import Haplotype
from .mhc_class import MhcClass
from .mhc_class_helpers import normalize_mhc_class_string
from .mutation import Mutation

from .parsing_helpers import (
    strip_whitespace_and_remove_quotes,
    strip_whitespace_and_dashes,
    split_allele_fields,
    contains_any_letters,
    contains_whitespace,
    smart_split,
    split_digits_at_end
)
from .result import Result
from .serotype import Serotype
from .species import Species, infer_species_from_prefix
from .allele_without_gene import AlleleWithoutGene

# default values for Parser parameters, reused in the 'parse' function below
DEFAULT_SPECIES_PREFIX = "HLA"
MAP_ALLELE_ALIASES = True
INFER_CLASS2_PAIRING = False
COLLAPSE_SINGLETON_HAPLOTYPES = True
COLLAPSE_SINGLETON_SEROTYPES = False
MAP_SPECIES_GROUP_TO_TOP_SPECIES = False
GENE_SEPS = "*_-^:"

class Parser(object):
    def __init__(
            self,
            map_allele_aliases=MAP_ALLELE_ALIASES,
            map_species_group_to_top_species=MAP_SPECIES_GROUP_TO_TOP_SPECIES,
            collapse_singleton_haplotypes=COLLAPSE_SINGLETON_HAPLOTYPES,
            collapse_singleton_serotypes=COLLAPSE_SINGLETON_SEROTYPES,
            gene_seps=GENE_SEPS):
        """
        map_allele_aliases : bool
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
        """
        self.map_allele_aliases = map_allele_aliases
        self.map_species_group_to_top_species = map_species_group_to_top_species
        self.collapse_singleton_haplotypes = collapse_singleton_haplotypes
        self.collapse_singleton_serotypes = collapse_singleton_serotypes
        self.gene_seps = gene_seps

    def parse_species_from_prefix(self, name):
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

    def parse_species(self, name, default_species=None):
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

    def _find_matching_name_and_parse_alleles(
            self,
            query_name: str,
            name_to_alleles_dict: Mapping[str, Sequence[str]],
            species : Species):
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
                candidate_names.append(
                    new_gene_name + query_name[len(old_gene_name):]
                )

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
                species,
                str_after_species=allele_name)
            allele = self.pick_best_result(candidates, raise_on_error=False)
            if allele is None:
                print("Warning: unable to parse allele name '%s' for '%s'" % (
                    allele_name,
                    normalized_name))
            else:
                alleles.append(allele)
        return (normalized_name, alleles)

    def get_serotype(self, species, serotype_name):
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
            query_name=serotype_name,
            name_to_alleles_dict=species.serotypes,
            species=species)

        if name_and_alleles is None:
            return None

        normalized_name, alleles = name_and_alleles

        return Serotype(
            species=species,
            name=normalized_name,
            alleles=alleles,
            raw_string=serotype_name)

    def get_haplotype_with_class2_locus(
            self, species, locus_string, haplotype_string):
        """
        Construct a haplotype limited at a specific Class II locus
        Returns Haplotype or None
        """
        locus = Class2Locus.get(species, locus_string)
        if locus is None:
            return None
        haplotype = self.get_haplotype(
            species,
            haplotype_string)
        if haplotype is None:
            return None
        return haplotype.restrict_class2_locus(
            class2_locus=locus,
            raise_on_error=False)

    def parse_haplotype_with_class2_locus_from_any_string_split(
            self, species, locus_and_haplotype):
        """
         Try parsing a string like "IAk" into the 'k' mouse haplotype restricted
         at the A locus
         """
        for locus_length in range(1, len(locus_and_haplotype)):
            haplotype_string = self.strip_extra_chars(
                locus_and_haplotype[locus_length:])
            locus_string = self.strip_extra_chars(
                locus_and_haplotype[:locus_length])
            haplotype = self.get_haplotype_with_class2_locus(
                species=species,
                locus_string=locus_string,
                haplotype_string=haplotype_string)
            if haplotype:
                return haplotype
        return None

    def get_haplotype(
            self,
            species,
            haplotype_name):
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
            query_name=haplotype_name,
            name_to_alleles_dict=species.haplotypes,
            species=species)

        if name_and_alleles is None:
            return None

        normalized_name, alleles = name_and_alleles

        return Haplotype(
            species=species,
            name=normalized_name,
            alleles=alleles,
            raw_string=haplotype_name)

    def parse_crossed_haplotypes(self, haplotype_name, default_species=None):
        if haplotype_name.count("/") != 1:
            return None

        if haplotype_name.count("-") != 1:
            return None
        species_prefix, haplotypes = haplotype_name.split("-")
        if haplotypes.count("/") != 1:
            return None
        first, second = haplotypes.split("/")
        parsed_first = self.parse_haplotype("%s-%s" % (species_prefix, first))
        if parsed_first is None:
            return None
        parsed_second = self.parse_haplotype("%s-%s" % (species_prefix, second))
        if parsed_second is None:
            return None
        return Haplotype(
            species=parsed_first.species,
            name="%s/%s" % (first, second),
            alleles=parsed_first.alleles + parsed_second.alleles,
            raw_string=haplotype_name)

    def parse_haplotype(
            self,
            haplotype_name,
            default_species=None):
        if "/" in haplotype_name:
            return self.parse_crossed_haplotypes(haplotype_name, default_species)

        # first try determining the species purley based on the string given
        # with reference to the default species
        species, remaining_string = self.parse_species(
            haplotype_name,
            default_species=None)
        if species:
            haplotype = self.get_haplotype(species, remaining_string)
            if haplotype:
                return haplotype

        # if this fails, try using the default species and also try
        # parsing the haplotype purely based on name
        matches = []
        species, remaining_string = self.parse_species(
            haplotype_name,
            default_species=default_species)

        if species:
            haplotype = self.get_haplotype(species, remaining_string)
            if haplotype:
                matches.append(haplotype)

        matches.extend(
            self.get_haplotypes_for_any_species(haplotype_name))

        if len(matches) == 0:
            return None
        return self.pick_best_result(matches)


    def get_haplotypes_for_any_species(self, haplotype_name):
        """
        Returns list of all haplotypes matching the given name
        """
        matches = []
        for (species_name, haplotype_dict) in raw_haplotypes_data.items():
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
            gene,
            allele_fields,
            functional_annotations=None):
        if allele_fields is None:
            return None

        if len(allele_fields) == 0:
            return gene

        if functional_annotations is None:
            allele_fields, functional_annotations = \
                parse_functional_annotations_from_allele_fields(allele_fields)


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
            if gene.is_chicken and not all([
                    (c.isdigit() or c == ".") for c in allele_field]):
                return None

        return Allele.get_with_gene(
            gene,
            allele_fields,
            functional_annotations)

    def get_gene_or_locus(self, species, name):
        fns = [Gene.get, Class2Locus.get]
        for fn in fns:
            result = fn(species, name)
            if result:
                return result
        return None

    def parse_gene_candidates_from_prefixes(self, species, seq):
        """
        Parse genes such as "A" or "DQB" and collect them with
        remaining string.

        Returns list of (gene_name, str_after_gene) pairs.
        """
        results = []
        for n in range(len(seq), 0, -1):
            substring = seq[:n]
            parsed = Gene.get(species, substring)
            if parsed:
                results.append((parsed, seq[n:]))
        return results

    compact_gene_and_allele_regex = re.compile("([A-Za-z]+)([0-9\:]+)[A-Z]?")

    def strip_extra_chars(self, seq):
        for sep in self.gene_seps:
            while seq.startswith(sep):
                seq = seq[1:]
        return strip_whitespace_and_dashes(seq)

    def parse_gene_candidates(
            self,
            species,
            str_after_species):
        """
        Returns set of pairs which can be (Gene, str) or (Class2Locus, str)

        """
        if contains_whitespace(str_after_species):
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
                    species, self.strip_extra_chars(str_after_species)))

            for sep in self.gene_seps:
                if str_after_species.count(sep) == 1:
                    gene_name, str_after_gene = smart_split(str_after_species, sep)
                    add_to_candidates(gene_name, str_after_gene)

            # If the string had neither "*" nor "_" then try to collect the gene
            # name as the non-numerical part at the start of the string.
            regex_match = Parser.compact_gene_and_allele_regex.fullmatch(str_after_species)
            if regex_match:
                gene_name, str_after_gene = regex_match.groups()
                add_to_candidates(gene_name, self.strip_extra_chars(str_after_gene))
        return list(set(candidates))

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
            combined = "%s-%s" % (first_part, next_part)
            if species.find_matching_gene_name(combined):
                parts_with_merged_gene_names.append(combined)
                i += 2
            else:
                parts_with_merged_gene_names.append(first_part)
                i += 1
        return parts_with_merged_gene_names

    def parse_allele_or_gene_candidates(
            self,
            species,
            str_after_species,
            original_name=None):
        # try to heuristically split apart the gene name and any allele information
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
        if str_after_species in species.allele_aliases:
            alias = species.allele_aliases[str_after_species]

            if alias is None:
                name = species.allele_aliases.original_key(str_after_species)
                allele = AlleleWithoutGene.get(
                    species=species,
                    name=name,
                    raw_string=str_after_species)
                candidate_results.append(allele)
            elif self.map_allele_aliases:
                parsed_alias = self.parse(
                    alias,
                    default_species=species,
                    raise_on_error=False)
                if parsed_alias is not None:
                    candidate_results.append(parsed_alias)

        for gene, allele_name in self.parse_gene_candidates(
                species, str_after_species):
            if gene is None:
                continue
            if len(allele_name) == 0:
                candidate_results.append(gene)
                continue

            allele = self.parse_allele_with_gene(gene, allele_name)
            if allele:
                if original_name:
                    allele = allele.copy(raw_string=original_name)
                candidate_results.append(allele)
        return candidate_results

    def pick_best_result(self, candidates, raise_on_error=True):
        if len(candidates) == 0:
            if raise_on_error:
                raise ValueError(
                    "Expected at least one candidate ParseResult object")
            else:
                return None

        elif len(candidates) == 1:
            return list(candidates)[0]

        def sort_key(candidate):
            if hasattr(candidate, 'name'):
                name_matches_raw_string = (
                    candidate.raw_string.lower() == candidate.name.lower())
            else:
                name_matches_raw_string = False
            is_class2_pair = type(candidate) is Class2Pair
            alpha_is_allele = is_class2_pair and type(candidate.alpha) is Allele
            alpha_is_valid = (
                is_class2_pair and type(candidate.alpha) in {Allele, AlleleWithoutGene, Gene}
            )
            beta_is_allele = is_class2_pair and type(candidate.beta) is Allele
            beta_is_valid = (
                is_class2_pair and type(candidate.beta) in {Allele, AlleleWithoutGene, Gene}
            )
            is_allele = type(candidate) is Allele
            is_serotype = type(candidate) is Serotype
            is_haplotype = type(candidate) is Haplotype
            is_gene = type(candidate) is Gene

            if is_allele:
                num_allele_fields = candidate.num_allele_fields
            elif is_class2_pair and alpha_is_allele and beta_is_allele:
                num_allele_fields = max(
                    candidate.alpha.num_allele_fields,
                    candidate.beta.num_allele_fields)
            else:
                num_allele_fields = 0

            if hasattr(candidate, 'gene'):
                raw_gene_name_matches_normalized = (
                    candidate.gene.raw_string.upper() ==
                    candidate.gene.name.upper()
                )
                original_gene_seq_length = len(candidate.gene.raw_string)
            elif is_gene:
                raw_gene_name_matches_normalized = (
                        candidate.raw_string.upper() ==
                        candidate.name.upper()
                )
                original_gene_seq_length = len(candidate.raw_string)
            else:
                raw_gene_name_matches_normalized = False
                original_gene_seq_length = 0

            if is_allele:
                allele_fields = candidate.allele_fields
            elif is_class2_pair and alpha_is_allele and beta_is_allele:
                allele_fields = (
                    candidate.alpha.allele_fields +
                    candidate.beta.allele_fields
                )
            else:
                allele_fields = ()

            allele_fields_normal = True
            for x in allele_fields:
                if not x.isdigit() or len(x) < 2 or len(x) > 4:
                    allele_fields_normal = False
                    break

            num_alleles_in_haplotype_or_serotype = 0
            if is_serotype or is_haplotype:
                num_alleles_in_haplotype_or_serotype = len(candidate.alleles)

            return (
                name_matches_raw_string,
                # for Class II pairs, prefer Allele objects for alpha and beta
                # and then any of {AlleleWithoutGene, Allele, Gene} where
                # genes play the role of mono-morphic alleles
                # TODO: optionally replace genes with known most common allele
                (is_class2_pair and alpha_is_allele and beta_is_allele),
                (is_class2_pair and alpha_is_valid and beta_is_valid),
                is_allele,
                allele_fields_normal,
                is_gene,
                raw_gene_name_matches_normalized,
                num_allele_fields,
                original_gene_seq_length,
                is_serotype,
                is_haplotype,
                num_alleles_in_haplotype_or_serotype,
                # make sure the ordering is stable by sorting on string
                # representation, even if it's semantically meaningful
                str(candidate),
            )
        sorted_candidates = sorted(candidates, key=sort_key, reverse=True)
        return sorted_candidates[0]

    def parse_allele_with_gene(self, gene, str_after_gene):
        if gene is None:
            return None

        if not str_after_gene:
            return None

        if contains_whitespace(str_after_gene):
            return None

        species = gene.species
        gene_name = gene.name
        if self.map_allele_aliases:
            # if the remaining string is an allele string which has
            # been renamed or deprecated, then get its new/canonical form
            # TODO: make this an optional transformation after parsing
            new_allele_name = species.allele_aliases.get(
                "%s*%s" % (gene_name, str_after_gene))
            if new_allele_name:
                gene_name, str_after_gene = new_allele_name.split("*")
        if species.is_mouse:
            if str_after_gene.isalnum() and not str_after_gene.isnumeric():
                # mouse alleles can be a mixture of numbers and letters
                # but can't be only numbers
                return Allele.get_with_gene(gene, str_after_gene.lower())
            else:
                return None
        elif species.is_rat:
            return Allele.get_with_gene(gene, str_after_gene.lower())
        elif species.is_pig:
            # parse e.g. "SLA-1-HB03" or "SLA-3-US#11"
            if str_after_gene[:2] == "HB" or "#" in str_after_gene:
                return Allele.get_with_gene(
                    gene,
                    str_after_gene.upper())
            elif contains_any_letters(str_after_gene):
                return Allele.get_with_gene(
                    gene,
                    str_after_gene.lower())
        # for now let's limit parsing of functional annotations to a single
        # letter at the end of an allele string following two or more numbers
        if len(str_after_gene) > 2 and (
                str_after_gene[-1].isalpha() and
                str_after_gene[-2].isdigit() and
                str_after_gene[-3].isdigit()):
            str_after_gene, functional_annotations = \
                parse_functional_annotations_from_seq(str_after_gene)
        else:
            functional_annotations = []
        # only allele names which allow three digits in second field seem to be
        # human class I names such as "HLA-B*15:120",
        # it's otherwise typical to allow three digits in the first field
        allow_three_digits_in_second_field = (
            species.is_human and gene.mhc_class == "Ia"
        )
        allow_three_digits_in_first_field = not allow_three_digits_in_second_field
        allele_fields = split_allele_fields(
            str_after_gene=str_after_gene,
            allow_three_digits_in_first_field=allow_three_digits_in_first_field,
            allow_three_digits_in_second_field=allow_three_digits_in_second_field)

        if allele_fields:
            return self.parse_allele_from_allele_fields(
                gene=gene,
                allele_fields=allele_fields,
                functional_annotations=functional_annotations)
        else:
            return None

    def parse_class2_pair_with_hyphen_sep(
            self,
            species,
            str_after_species):
        """
        If possible, try parsing allele pair with a single hyphen separator,
        e.g. DRA1*01:01-DRB1*01:01
        """
        hyphen_parts = self.split_by_hyphen_except_gene_names(
            species,
            str_after_species)

        if len(hyphen_parts) == 2:
            # this situation is tricky since it might be either
            # a class II allele pair
            #   e.g. DRA1*01:01-DRB1*01:01
            # or a class I allele where '-' is used instead of '*'
            #   e.g. 1-HB01 (swine allele)
            alpha, beta = hyphen_parts
            return self.parse_class2_pair_from_alpha_and_beta_strings(
                alpha,
                beta,
                default_species=species)
        return None

    def parse_class2_pair_with_slash_sep(
            self,
            name,
            default_species=None):
        if name.count("/") == 1:
            # parse paired Class II alleles such as 'DRA1*01:01/DRB1*01:01'
            alpha, beta = name.split("/")
            return self.parse_class2_pair_from_alpha_and_beta_strings(
                alpha,
                beta,
                default_species=default_species)
        return None

    def parse_class2_pair_from_alpha_and_beta_strings(
            self,
            alpha,
            beta,
            default_species=None,
            require_alleles=False):
        """
        If a name is known to contain "/" then it's
        expected to be of a format like:
            HLA-DQA*01:01/DQB*01:02

        The species information from the first allele
        is used to guide parsing for the second allele.
        """
        alpha_result = self.parse(
            alpha,
            infer_class2_pairing=False,
            default_species=default_species,
            raise_on_error=False)

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
            beta,
            default_species=species_for_beta,
            infer_class2_pairing=False,
            raise_on_error=False)
        if beta_result is None:
            return None
        elif require_alleles and type(beta_result) is not Allele:
            return None
        if alpha_result.species != beta_result.species:
            return None
        return Class2Pair(alpha_result, beta_result)

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
            mut =  Mutation.parse(mutation_string, raise_on_error=False)
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
            gene_to_mutations):
        n_mutations = len(mutations_without_selector) + len(gene_to_mutations) + len(chain_to_mutations)
        if n_mutations == 0:
            return None
        result = result_without_mutation

        alpha_mutations = chain_to_mutations["alpha"]
        beta_mutations = chain_to_mutations["beta"]

        if type(result) is Allele:
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
                mutations.extend(mutations_without_selector)
            result = result.copy_with_extra_mutations(mutations)
        elif type(result) is Class2Pair:
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
            self,
            result_without_mutation,
            mutation_strings,
            default_species=None,
            original_name=None):
        """
        Parameters
        ----------
        result_without_mutation : Result

        mutation_strings : list[str]

        default_species : str or None

        Returns Allele
        """
        if type(result_without_mutation) in (Serotype, Haplotype):
            result_without_mutation = result_without_mutation.collapse_if_possible()

        if result_without_mutation is None:
            return None

        if type(result_without_mutation) not in (Allele, Class2Pair):
            return None

        if mutation_strings[-1].lower() != "mutant":
            return None
        mutation_strings = mutation_strings[:-1]

        if len(mutation_strings) == 0:
            return None

        mutations_without_selector, chain_to_mutations, gene_to_mutations = \
            self.parse_mutations(
                species=result_without_mutation.species,
                mutation_strings=mutation_strings)

        return self.apply_mutations(
            result_without_mutation,
            mutations_without_selector,
            chain_to_mutations,
            gene_to_mutations)

    def parse_with_interior_whitespace(
            self,
            name,
            default_species=DEFAULT_SPECIES_PREFIX,
            raise_on_error=False):
        """
        If there's whitespace within an allele description then it's
        either a mutant allele or an error.
        """
        parts = [p.strip() for p in name.lower().split() if p]

        if len(parts) == 1:
            # no whitespace, so nothing else in this function applies
            return None

        if "mutant" in parts:
            result_without_mutation = self.parse(
                parts[0],
                default_species=default_species,
                raise_on_error=False)
            if result_without_mutation is None:
                return None
            return self.parse_and_apply_mutations(
                result_without_mutation=result_without_mutation,
                mutation_strings=parts[1:],
                original_name=name,
                default_species=default_species)

        if len(parts) == 2:
            species_common_name, gene_or_locus_name = parts
            gene_or_locus = self.get_gene_or_locus(
                species_common_name,
                gene_or_locus_name)

            if gene_or_locus:
                return gene_or_locus
            elif raise_on_error:
                raise ParseError(
                    "Failed to parse '%s' as gene in '%s'" % (
                        gene_or_locus, name))
            else:
                return None
        elif len(parts) >= 3:
            if parts[-2] == "class" and parts[-1] in {"1", "2", "i", "ii"}:

                mhc_class_string = normalize_mhc_class_string(parts[-1])
                # Parse MHC classes, haplotypes, or serotypes such as:
                # - "HLA class I"
                # - "H2-b class I"
                # - "ELA-A1 class I"
                # - "H2-r class I"
                # - "BF19 class II"
                unrestricted_string = " ".join(parts[:-2])
                for unrestricted_result in self.parse_multiple_candidates(
                        unrestricted_string,
                        default_species=default_species):
                    if type(unrestricted_result) is Haplotype:
                        return unrestricted_result.restrict_mhc_class(
                            mhc_class_string)
                    elif type(unrestricted_result) is Species:
                        return MhcClass(unrestricted_result, mhc_class_string)
                if raise_on_error:
                    raise ParseError(
                            "Unable to parse '%s' in '%s'" % (
                                unrestricted_string,
                                name,))
                else:
                    return None
        if raise_on_error:
            raise ParseError("Unexpected whitespace in '%s'" % name)
        else:
            return None

    def transform_parse_candidates(self, parse_candidates, original_name):
        """
        Annotate every ParseResult in a list with its `raw_string` field
        updated to `original_name`.

        Also perform optional transformations such as collapsing singleton
        serotypes and haplotypes.
        """
        results = []
        for parse_candidate in parse_candidates:
            if parse_candidate is None:
                continue
            t = type(parse_candidate)
            if ((self.collapse_singleton_haplotypes and t is Haplotype) or
                    (self.collapse_singleton_serotypes and t is Serotype)):
                simpler_result = parse_candidate.collapse_if_possible()
                if simpler_result:
                    parse_candidate = simpler_result
            parse_candidate = parse_candidate.copy(raw_string=original_name)
            assert parse_candidate is not None
            results.append(parse_candidate)
        return list(set(results))

    def parse_gene_without_species(self, gene_name, default_species=None):
        """
        Parse the gene name without any associated species based on being
        either a unique gene name across all species or matching the default
        species.

        Returns Species or None
        """
        species = None
        species_candidates = Species.get_species_with_gene_name(gene_name)
        if len(species_candidates) > 1 and default_species is not None:
            if default_species in species_candidates:
                species = default_species
        if len(species_candidates) == 1:
            species = species_candidates[0]
        if species is None:
            return None
        return Gene.get(species, gene_name)

    def parse_allele_without_species(self, allele_name, default_species=None):
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
                gene_name=gene_name, default_species=default_species)
            if gene:
                return self.parse_allele_or_gene_candidates(
                    species=gene.species,
                    str_after_species=allele_name,
                    original_name=allele_name)
        return None

    def parse_multiple_candidates(
            self,
            name,
            original_name=None,
            default_species=DEFAULT_SPECIES_PREFIX):
        """
        Returns list of ParseResult objects which are candidate interpretations
        of the given string.
        """
        if original_name is None:
            original_name = name

        # list containing all candidate results
        parse_candidates = []

        # all of these functions are expected to take the sequence
        # without any additional knowledge of which species it is associated
        # with.
        fns_without_species = [
            self.parse_class2_pair_with_slash_sep,
            self.parse_with_interior_whitespace,
            self.parse_haplotype,
            self.parse_gene_without_species,
            self.parse_allele_without_species,
        ]
        for fn in fns_without_species:
            result = fn(
                name,
                default_species=default_species)

            if not result:
                continue
            if type(result) in (list, tuple):
                parse_candidates.extend(result)
            elif isinstance(result, Result):
                parse_candidates.append(result)
            else:
                raise ParseError("Unexpected result '%s' while parsing '%s'" % (
                    result,
                    original_name))

        species, str_after_species = self.parse_species(
            name,
            default_species=default_species)

        if species is not None:
            if len(str_after_species) == 0:
                parse_candidates.append(species)
            else:
                # all of these functions are expected to take two arguments
                # (Species, str_after_species) and returns either a parsed
                # represntation or None
                fns_with_species = [
                    Class2Locus.get,
                    Gene.get,
                    self.get_serotype,
                    self.get_haplotype,
                    self.parse_allele_or_gene_candidates,
                    self.parse_class2_pair_with_hyphen_sep,
                    self.parse_haplotype_with_class2_locus_from_any_string_split,
                ]

                for fn in fns_with_species:
                    result = fn(
                        species,
                        str_after_species)

                    if not result:
                        continue
                    if type(result) in (list, tuple):
                        parse_candidates.extend(result)
                    elif isinstance(result, Result):
                        parse_candidates.append(result)
                    else:
                        raise ParseError("Unexpected result '%s' while parsing '%s'" % (
                            result,
                            original_name))

        # update all the objects to set their raw_string field to original_name
        # and also perform optional transformations
        parse_candidates = self.transform_parse_candidates(
            parse_candidates,
            original_name=original_name)

        return parse_candidates


    @cache
    def parse(
            self,
            name,
            infer_class2_pairing=INFER_CLASS2_PAIRING,
            default_species=DEFAULT_SPECIES_PREFIX,
            preferred_type=None,
            raise_on_error=True):
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

        default_species : Species or None
            Assume this species if it's not obvious in the sequence.

        preferred_type : type
            If a result of this class is available, return it.

        raise_on_error : bool
            If False, return False when parsing is impossible.

        Returns object with one of the following types:
            - Species
            - MhcClass
            - Gene
            - Allele
            - Class2Pair
        """
        trimmed_name = strip_whitespace_and_remove_quotes(name)

        if len(trimmed_name) == 0:
            if raise_on_error:
                raise ParseError("Cannot parse empty allele name '%s'" % name)
            else:
                return None

        candidates = self.parse_multiple_candidates(
            name,
            default_species=default_species)

        if len(candidates) == 0:
            if raise_on_error:
                raise ParseError("Could not parse '%s'" % name)
            else:
                return None

        if preferred_type is not None:
            candidates_with_preferred_type = [
                candidate for candidate in candidates
                if isinstance(candidate, preferred_type)
            ]
            if len(candidates_with_preferred_type) > 0:
                candidates = candidates_with_preferred_type

        result = self.pick_best_result(candidates)
        if infer_class2_pairing:
            result = infer_class2_alpha_chain(result)
        return result.copy(raw_string=name)

