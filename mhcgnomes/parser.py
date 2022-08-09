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
from typing import Mapping, Iterable, Union, Sequence

from .allele import Allele
from .allele_annotations import (
    parse_annotations_from_seq,
    parse_annotations_from_allele_fields
)
from .allele_without_gene import AlleleWithoutGene
from .class2_locus import Class2Locus
from .pair import Pair, infer_class2_alpha_chain
from .common import cache, unique
from .data import haplotypes as raw_haplotypes_data
from .errors import ParseError
from .gene import Gene
from .haplotype import Haplotype
from .mhc_class import MhcClass
from .mutation import Mutation
from .parsing_helpers import (
    strip_whitespace_and_dashes,
    split_allele_fields,
    contains_any_letters,
    contains_whitespace,
    smart_split,
    split_digits_at_end,
)
from .result import Result
from .result_with_species import ResultWithSpecies
from .result_sorting import pick_best_result
from .serotype import Serotype
from .species import Species, infer_species_from_prefix, find_matching_species_objects
from .standard_format import parse_standard_allele_format
from .token import Token
from .tokenize import tokenize


# default values for Parser parameters, reused in the 'parse' function below
DEFAULT_SPECIES_PREFIX = "HLA"
USE_ALLELE_ALIASES = False
INFER_CLASS2_PAIRING = False
COLLAPSE_SINGLETON_HAPLOTYPES = True
COLLAPSE_SINGLETON_SEROTYPES = False
MAP_SPECIES_GROUP_TO_TOP_SPECIES = False
GENE_SEPS = "*_-^:"

class Parser(object):
    def __init__(
            self,
            use_allele_aliases: bool = USE_ALLELE_ALIASES,
            map_species_group_to_top_species: bool = MAP_SPECIES_GROUP_TO_TOP_SPECIES,
            collapse_singleton_haplotypes: bool = COLLAPSE_SINGLETON_HAPLOTYPES,
            collapse_singleton_serotypes: bool = COLLAPSE_SINGLETON_SEROTYPES,
            gene_seps: Sequence[str] = GENE_SEPS,
            verbose=False):
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

    def parse_species(
            self,
            name: str,
            default_species: Union[Species, str, None] = None):
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
            query_name : str,
            name_to_alleles_dict : Mapping[str, Sequence[str]],
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

            allele = pick_best_result(candidates, raise_on_error=False)
            if allele is None:
                print("Warning: unable to parse allele name '%s' for '%s'" % (
                    allele_name,
                    normalized_name))
            else:
                alleles.append(allele)
        return (normalized_name, alleles)

    def get_serotype(
            self,
            species: Union[Species, str],
            serotype_name: str):
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

    def parse_haplotype_with_class2_locus_from_any_string_split(
            self,
            species: Union[Species, str],
            locus_and_haplotype: str):
        """
         Try parsing a string like "IAk" into the 'k' mouse haplotype restricted
         at the A locus
         """
        for locus_length in range(
                1,
                len(locus_and_haplotype)):
            locus_string = self.strip_extra_chars(
                locus_and_haplotype[:locus_length])
            locus = Class2Locus.get(species, locus_string)
            if locus is None:
                continue
            haplotype_string = self.strip_extra_chars(
                locus_and_haplotype[locus_length:])
            haplotype = self.get_haplotype(
                species,
                haplotype_string)
            if haplotype is None:
                continue
            haplotype = haplotype.restrict_class2_locus(
                class2_locus=locus,
                raise_on_error=False)
            if haplotype:
                return haplotype
        return None

    def get_haplotype(
            self,
            species: Union[Species, str],
            haplotype_name: str):
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

    def create_crossed_haplotype(
            self,
            first_haplotype_object: Haplotype,
            second_haplotype_name: str):
        if first_haplotype_object is None:
            return None
        if len(second_haplotype_name) == 0:
            return None
        if not second_haplotype_name.isalnum():
            return None
        second_haplotype_object = self.get_haplotype(
            first_haplotype_object.species,
            second_haplotype_name)

        if second_haplotype_object is None:
            return None
        name = "%s/%s" % (first_haplotype_object.name, second_haplotype_object.name)
        raw_string = "%s/%s" % (first_haplotype_object.raw_string, second_haplotype_name)
        return Haplotype(
            species=first_haplotype_object.species,
            name=name,
            alleles=first_haplotype_object.alleles + second_haplotype_object.alleles,
            raw_string=raw_string)


    def parse_haplotype(
            self,
            haplotype_name: str,
            default_species: Union[Species, str, None] = None):

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
        return pick_best_result(matches)


    def get_haplotypes_for_any_species(
            self,
            haplotype_name: str) -> Sequence[Haplotype]:
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
            gene: Gene,
            allele_fields: Union[str, Sequence[str], None],
            functional_annotations: Union[str, Sequence[str], None] = None,
            raw_string: Union[str, None] = None) -> Union[Gene, Allele, None]:
        if allele_fields is None:
            return None

        if len(allele_fields) == 0:
            return gene

        if functional_annotations is None:
            allele_fields, functional_annotations = \
                parse_annotations_from_allele_fields(allele_fields)


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
            annotations=functional_annotations,
            raw_string=raw_string)

    def get_gene_or_locus(self, species: Union[Species, str], name : str):
        fns = [Gene.get, Class2Locus.get]
        for fn in fns:
            result = fn(species, name)
            if result:
                return result
        return None

    def parse_gene_candidates_from_prefixes(
            self,
            species: Union[Species, str],
            seq: str):
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

    compact_gene_and_allele_regex = re.compile("([A-Za-z]+)([0-9\:]+[A-Z]?)")

    def strip_extra_chars(self, seq: str):
        for sep in self.gene_seps:
            while seq.startswith(sep):
                seq = seq[1:]
        return strip_whitespace_and_dashes(seq)

    def parse_gene_candidates(
            self,
            species: Union[Species, str],
            str_after_species: str) -> Sequence[Gene]:
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
            # just split_token_sequences on the '*' character and return this as the
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
            raw_string=None):
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

        known_allele = species.get_known_allele(
            gene_name=None, allele_name=str_after_species)

        if known_allele is not None:
            gene_name, allele_name = known_allele
            assert gene_name is None
            if "*" not in allele_name:
                candidate_results.append(
                    AlleleWithoutGene.get(
                        species=species,
                        name=allele_name,
                        raw_string=str_after_species))

        for gene, allele_name in self.parse_gene_candidates(
                species, str_after_species):
            if gene is None:
                continue
            if len(allele_name) == 0:
                candidate_results.append(gene)
                continue

            allele = self.parse_allele_with_gene(
                gene, allele_name, raw_string=raw_string)
            if allele:
                candidate_results.append(allele)
        return candidate_results

    def parse_allele_with_gene(
            self,
            gene: Gene,
            str_after_gene: str,
            preserve_caps: bool = False,
            raw_string: Union[str, None] = None):
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
                    raw_string=raw_string)
            else:
                return None
        elif species.is_rat:
            return Allele.get_with_gene(
                gene,
                str_after_gene if preserve_caps else str_after_gene.lower(),
                raw_string=raw_string)
        elif species.is_pig:
            # parse e.g. "SLA-3-US#11"
            if "#" in str_after_gene:
                return Allele.get_with_gene(
                    gene,
                    str_after_gene if preserve_caps else str_after_gene.upper(),
                    raw_string=raw_string)
            elif contains_any_letters(str_after_gene):
                return Allele.get_with_gene(
                    gene,
                    str_after_gene if preserve_caps else str_after_gene.lower(),
                    raw_string=raw_string)
        str_after_gene, prefix_annotations, functional_annotations = \
            parse_annotations_from_seq(str_after_gene)
        # only allele names which allow three digits in second field seem to be
        # human class I names such as "HLA-B*15:120" but not Ic/Id genes
        # like MICA.
        # For human class II genes it seems like DPB1 is the only one using
        # three digits in the first field
        allow_three_digits_in_second_field = (
            species.is_human and (
                gene.mhc_class in {"I", "Ia", "Ib"} or
                not gene.name.startswith("DP"))
        )

        allow_three_digits_in_first_field = not allow_three_digits_in_second_field
        allele_fields = split_allele_fields(
            str_after_gene=str_after_gene,
            allow_three_digits_in_first_field=allow_three_digits_in_first_field,
            allow_three_digits_in_second_field=allow_three_digits_in_second_field)

        if allele_fields:
            # for now we only expect a "W" prefix annotation, indicating
            # that it's a workshop allele, so we just put that back in the
            # sequence.
            first_field = "".join(prefix_annotations) + allele_fields[0]
            allele_fields = (first_field,) + tuple(allele_fields[1:])
            return self.parse_allele_from_allele_fields(
                gene=gene,
                allele_fields=allele_fields,
                functional_annotations=functional_annotations,
                raw_string=raw_string)
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
            gene_to_mutations):
        n_mutations = (
                len(mutations_without_selector) +
                len(gene_to_mutations) +
                len(chain_to_mutations))

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
            self,
            result_without_mutation: Union[Gene, Allele, Pair],
            mutation_tokens: Sequence[Token]) -> Union[Allele, Pair, None]:
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

        if type(result_without_mutation) not in (Gene, Allele, Pair):
            return None

        while mutation_tokens[-1].is_mutant:
            mutation_tokens = mutation_tokens[:-1]

        if len(mutation_tokens) == 0:
            return None

        mutation_strings = [tok.seq for tok in mutation_tokens]

        mutations_without_selector, chain_to_mutations, gene_to_mutations = \
            self.parse_mutations(
                species=result_without_mutation.species,
                mutation_strings=mutation_strings)

        return self.apply_mutations(
            result_without_mutation,
            mutations_without_selector,
            chain_to_mutations,
            gene_to_mutations)


    def adjust_raw_strings(
            self,
            candidates: Sequence[Result],
            raw_string: str):
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

    def transform_parse_candidate(
            self,
            parse_candidate: Result):
        """
        Perform optional transformations on Result objects such as collapsing
        singleton serotypes and haplotypes.
        """
        if parse_candidate is None:
            return None
        if parse_candidate in self._transform_cache:
            return self._transform_cache[parse_candidate]
        t = type(parse_candidate)
        transformed = None
        if t in (Serotype, Haplotype):
            old_alleles = parse_candidate.alleles
            new_alleles = self.transform_parse_candidates(old_alleles)
            if old_alleles != new_alleles:
                transformed = parse_candidate.copy(alleles=new_alleles)
            if (
                    (self.collapse_singleton_haplotypes and t is Haplotype) or
                    (self.collapse_singleton_serotypes and t is Serotype)):
                if transformed is None:
                    transformed = parse_candidate.collapse_if_possible()
                else:
                    transformed = transformed.collapse_if_possible()
        elif t is Pair:
            alpha = self.transform_parse_candidate(parse_candidate.alpha)
            beta = self.transform_parse_candidate(parse_candidate.beta)
            if alpha != parse_candidate.alpha or beta != parse_candidate.beta:
                transformed = Pair.get(
                    alpha,
                    beta,
                    raw_string=parse_candidate.raw_string)
        elif t in (AlleleWithoutGene, Allele):
            raw_string = parse_candidate.raw_string
            species = parse_candidate.species
            if t is Allele:
                gene = parse_candidate.gene
                gene_name = gene.name
            else:
                gene = gene_name = None
            old_name = parse_candidate.name
            transformed = None
            if self.use_allele_aliases:
                allele_alias = species.get_allele_alias(
                    gene_name=gene_name,
                    allele_name=old_name)

                if allele_alias is not None:
                    new_gene_name, new_allele_name = allele_alias
                    if new_gene_name is None:
                        if "*" not in new_allele_name:
                            transformed = AlleleWithoutGene.get(
                                species,
                                new_allele_name,
                                raw_string=raw_string)
                    else:
                        if new_gene_name == gene_name:
                            new_gene = gene
                        else:
                            new_gene = Gene.get(species, new_gene_name)
                        transformed = self.parse_allele_with_gene(
                            new_gene,
                            new_allele_name,
                            preserve_caps=True,
                            raw_string=raw_string)

            if transformed is None:
                known_allele = species.get_known_allele(
                    gene_name=gene_name,
                    allele_name=old_name)
                if known_allele is not None:
                    new_gene_name, new_allele_name = known_allele
                    if new_gene_name is None:
                        if "*" not in new_allele_name:
                            transformed = AlleleWithoutGene.get(
                                species,
                                new_allele_name,
                                raw_string=raw_string)
                    else:
                        if new_gene_name == gene_name:
                            new_gene = gene
                        else:
                            new_gene = Gene.get(species, new_gene_name)
                        transformed = self.parse_allele_with_gene(
                            new_gene,
                            new_allele_name,
                            preserve_caps=True,
                            raw_string=raw_string)
        if self.verbose:
            print("=== Transform ===")
            print("In:  %s" % parse_candidate)
            print("Out: %s" % transformed)
        if transformed is not None:
            result = transformed
        else:
            result = parse_candidate
        self._transform_cache[parse_candidate] = result
        return result

    def transform_parse_candidates(
            self,
            parse_candidates: Sequence[Result]):
        """
        Apply transform_parse_candidate to a list of results.
        """
        results = []
        for parse_candidate in parse_candidates:
            result = self.transform_parse_candidate(parse_candidate)
            if result:
                results.append(result)
        return unique(results)

    def parse_gene_without_species(
            self,
            gene_name: str,
            default_species: Union[Sequence, str, None] = None):
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

    def parse_allele_without_species(
            self,
            allele_name : str,
            default_species : Union[str, Species, None]=None):
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
                    raw_string=allele_name)
        return None


    def parse_single_token_to_multiple_candidates(
            self,
            token: Token,
            default_species: Union[str, Species, None]=DEFAULT_SPECIES_PREFIX):
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

        seq = token.seq
        raw_string = token.raw_string

        standard_result = parse_standard_allele_format(
            seq,
            raw_string=raw_string,
            default_species=default_species)

        if standard_result:
            if self.verbose:
                print(f"""=== Standard format result """)
                print(standard_result)
            return [standard_result]

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
            result = fn(seq, default_species=default_species)

            if self.verbose:
                print("%s('%s', default_species=%s) = %s" % (
                    fn.__qualname__,
                    seq,
                    ('%s' % default_species if type(default_species) is str
                        else default_species),
                    ('%s' % result if type(result) is str else result)
                ))
            if result is None:
                continue
            if type(result) in (list, tuple):
                parse_candidates.extend(result)
            elif isinstance(result, Result):
                parse_candidates.append(result)


        species, str_after_species = self.parse_species(
            name=seq,
            default_species=default_species)

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
                    if self.verbose:
                        print("%s(%s, '%s') = %s" % (
                            fn.__qualname__,
                            species,
                            seq,
                            "None" if not result else '%s' % result
                        ))
                    if result is None:
                        continue
                    if type(result) in (list, tuple):
                        parse_candidates.extend(result)
                    elif isinstance(result, Result):
                        parse_candidates.append(result)
                    else:
                        raise ParseError("Unexpected result '%s' while parsing '%s'" % (
                            result,
                            raw_string))
        parse_candidates = unique(parse_candidates)
        # update all the objects to set their raw_string field to raw_string
        # and also perform optional transformations
        return self.adjust_raw_strings(
            parse_candidates,
            raw_string=raw_string)

    def restrict_result_type_if_possible(
            self,
            results : Sequence[Result],
            preferred_types : Sequence[type]):
        """
        Filter results to any of given types, as long as some results remain.
        Otherwise return all results.
        """
        if type(preferred_types) not in (list, set, tuple):
            preferred_types = [preferred_types]
        if type(preferred_types) is not tuple:
            preferred_types = tuple(preferred_types)
        filtered_results = [
            result
            for result in results
            if isinstance(result, preferred_types)
        ]
        if filtered_results:
            return filtered_results
        else:
            return results

    def parse_with_class_token_to_multiple_candidates(
            self,
            class_token: Token,
            other_tokens: Sequence[Token],
            default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX):
        class1 = class_token.is_class1
        class2 = class_token.is_class2
        mhc_class_string = "I" if class1 else "II"

        candidates = []
        if len(other_tokens) == 0:
            mhc_class = MhcClass.get(
                default_species,
                mhc_class_string)
            if mhc_class:
                candidates.append(mhc_class)
        else:
            for unrestricted_result in self.parse_tokens_to_multiple_candidates(
                    tokens=other_tokens,
                    default_species=default_species):
                t = type(unrestricted_result)
                if t is Haplotype:
                    restricted = unrestricted_result.restrict_mhc_class(mhc_class_string)
                    if restricted:
                        candidates.append(restricted)
                elif t is Species:
                    mhc_class = MhcClass.get(
                        unrestricted_result,
                        mhc_class_string)
                    if mhc_class:
                        candidates.append(mhc_class)
                elif unrestricted_result.has_mhc_class:
                    if (class1 and unrestricted_result.is_class1) or (class2 and unrestricted_result.is_class2):
                        candidates.append(unrestricted_result)
        return unique(candidates)

    def parse_with_haplotype_token_to_multiple_candidates(
            self,
            maybe_species_token: Token,
            other_tokens: Sequence[Token],
            default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX):
        """
        Parse "Haplotype H2 L-q" but also "Haplotype H2-k"
        Or: "L-q H2 Haplotype"
        Returns list of results
        """
        candidates = []
        # First try parsing the second token as a species:
        species = Species.get(maybe_species_token)
        if not species:
            return self.restrict_result_type_if_possible(
                results=self.parse_tokens_to_multiple_candidates(
                    tokens=(maybe_species_token,) + other_tokens,
                    default_species=default_species),
                preferred_types=[Haplotype])

        if not other_tokens:
            # sequences like "haplotype H2" just map to the species
            return [species]

        return self.parse_tokens_to_multiple_candidates(
            tokens=other_tokens,
            default_species=species)


    def parse_tokens_around_slash(
            self,
            tokens_before: Sequence[Token],
            tokens_after: Sequence[Token],
            default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX):
        if len(tokens_before) == 0:
            return self.parse_tokens_to_multiple_candidates(
                tokens=tokens_after,
                default_species=default_species)
        elif len(tokens_after) == 0:
            return self.parse_tokens_to_multiple_candidates(
                tokens=tokens_before,
                default_species=default_species)
        candidates = []
        for result_before in self.parse_tokens_to_multiple_candidates(
                tokens=tokens_before,
                default_species=default_species):
            if result_before is None:
                continue
            if type(result_before) is Haplotype:
                if len(tokens_after) not in {1, 2}:
                    continue
                if tokens_after[0].can_be_identifier:
                    haplotype = self.create_crossed_haplotype(
                        first_haplotype_object=result_before,
                        second_haplotype_name=tokens_after[0].seq)
                    if haplotype is None:
                        continue
                    elif len(tokens_after) == 1:
                        candidates.append(haplotype)
                    elif len(tokens_after) == 2 and tokens_after[1].is_class1_or_class2:
                        class1 = tokens_after[1].is_class1
                        restricted_haplotype = haplotype.restrict_mhc_class(
                            class_restriction="I" if class1 else "II")
                        if restricted_haplotype:
                            candidates.append(restricted_haplotype)
            elif type(result_before) in (Allele, Gene):
                if result_before.has_species:
                    species = result_before.species
                else:
                    species = default_species
                for result_after in self.parse_tokens_to_multiple_candidates(
                        tokens=tokens_after,
                        default_species=species):
                    if result_after is None:
                        continue
                    if result_before.species != result_after.species:
                        continue
                    class2_pair = Pair.get(result_before, result_after)
                    if class2_pair:
                        candidates.append(class2_pair)
        return unique(candidates)

    def parse_tokens_to_multiple_candidates(
            self,
            tokens: Sequence[Token],
            default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX):

        if len(tokens) == 0:
            return []
        elif len(tokens) == 1:
            # no whitespace, so nothing else in this function applies
            return self.parse_single_token_to_multiple_candidates(
                token=tokens[0],
                default_species=default_species)
        elif "/" in tokens:
            slash_index = tokens.index("/")
            return self.parse_tokens_around_slash(
                tokens_before=tokens[:slash_index],
                tokens_after=tokens[slash_index + 1:],
                default_species=default_species)

        # if the token sequence didn't start with a recognizable species name
        # then continue here
        candidates = []
        if tokens[-1].is_alpha:
            for candidate in self.parse_tokens_to_multiple_candidates(
                    tokens=tokens[:-1],
                    default_species=default_species):
                if type(candidate) in (Allele, AlleleWithoutGene, Gene):
                    if candidate.is_class1 or candidate.is_class2_alpha:
                        candidates.append(candidate)
                    elif type(candidate) is Pair:
                        candidates.append(candidate.alpha)
                    elif type(candidate) is Class2Locus:
                        alpha_genes = candidate.alpha_chain_genes
                        if len(alpha_genes) == 1:
                            candidates.append(alpha_genes[0])
                    else:
                        continue
        elif tokens[-1].is_beta:
            for candidate in self.parse_tokens_to_multiple_candidates(
                    tokens=tokens[:-1],
                    default_species=default_species):
                if type(candidate) in (Allele, AlleleWithoutGene, Gene):
                    if candidate.is_class2_beta:
                        candidates.append(candidate)
                    elif type(candidate) is Pair:
                        candidates.append(candidate.beta)
                    elif type(candidate) is Class2Locus:
                        beta_genes = candidate.beta_chain_genes
                        if len(beta_genes) == 1:
                            candidates.append(beta_genes[0])
                    else:
                        continue
        elif tokens[-1].is_mutant:
            for without_mutation in self.parse_single_token_to_multiple_candidates(
                    token=tokens[0],
                    default_species=default_species):
                if not without_mutation:
                    continue
                with_mutation = self.parse_and_apply_mutations(
                    result_without_mutation=without_mutation,
                    mutation_tokens=tokens[1:-1])
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
                    default_species=default_species))
        elif tokens[0].is_class1_or_class2:
            # Parse MHC classes, haplotypes, or serotypes such as:
            # - "class I HLA" => tokenized as ("class-1", "hla)
            # - "Class I H2-b " => tokenized as ("class-1", "h2-b")
            candidates.extend(
                self.parse_with_class_token_to_multiple_candidates(
                    class_token=tokens[0],
                    other_tokens=tokens[1:],
                    default_species=default_species))

        elif len(tokens) >= 3 and tokens[1].is_class1_or_class2:
            # parse strings like "MOUSE MHC class I L-q" as an allele
            # Tokenization normalizes this sequence into:
            #   ("mouse", "class-1", "L-q")

            species = Species.get(tokens[0].seq)

            if species:
                class1 = tokens[1].is_class1
                class2 = tokens[1].is_class2
                mhc_class_string = "I" if class1 else "II"
                for candidate in self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[2:],
                        default_species=species):

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
                    default_species=default_species))

        elif tokens[-1].is_haplotype:
            # parse "L-q H2 haplotype" but also "H2-k haplotype"
            candidates.extend(
                self.parse_with_haplotype_token_to_multiple_candidates(
                    maybe_species_token=tokens[-2],
                    other_tokens=tokens[:-2],
                    default_species=default_species))
        elif tokens[-1].is_gene:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[:-1],
                        default_species=default_species),
                    preferred_types=[Gene]))
        elif tokens[0].is_gene:
            candidates.extend(
                self.restrict_result_type_if_possible(
                    results=self.parse_tokens_to_multiple_candidates(
                        tokens=tokens[1:],
                        default_species=default_species),
                    preferred_types=[Gene]))
        elif len(tokens) == 2:
            first_token, second_token = tokens
            for first_result in self.parse_single_token_to_multiple_candidates(
                    token=first_token,
                    default_species=default_species):
                if type(first_result) is Species:
                    for second_result in self.parse_single_token_to_multiple_candidates(
                            token=second_token,
                            default_species=first_result):
                        if isinstance(second_result, ResultWithSpecies):
                            if second_result.species == first_result:
                                candidates.append(second_result)
        return self.transform_parse_candidates(candidates)

    def select_species_from_optional_attributes(
            self,
            attributes: Mapping[str, str]):
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
            self,
            name: str,
            default_species: Union[Species, str, None]=DEFAULT_SPECIES_PREFIX):
        """
        Returns list of ParseResult objects which are candidate interpretations
        of the given string.
        """
        tokenization_result = tokenize(name)
        if len(tokenization_result.trimmed_string) == 0:
            return []

        tokens = tokenization_result.tokens
        species_candidates = []
        found_species_prefix = False
        for num_species_tokens in [3, 2, 1]:
            if len(tokens) >= (num_species_tokens + 1):
                # try peeling off species names such as
                # "homo sapiens" at the beginning of a token sequence
                species_candidates = find_matching_species_objects(
                    ' '.join([t.seq for t in tokens[:num_species_tokens]]))
            if len(species_candidates) > 0:
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
            else:
                for maybe_species in species_candidates:
                    if len(tokens) == 1 and tokens[0].is_class1:
                            results.append(MhcClass.get(maybe_species, "I"))
                    elif len(tokens) == 1 and tokens[0].is_class2:
                            results.append(MhcClass.get(maybe_species, "II"))
                    else:
                        maybe_results = self.parse_tokens_to_multiple_candidates(
                            tokens=tokens,
                            default_species=maybe_species)
                        # filter out the Species hits since we already have a species from
                        # the prefix
                        maybe_results = [r for r in maybe_results if type(r) is not Species]
                        results.extend(maybe_results)
        else:
            # species represented in some UniProt entries using 'OS=' attribute
            species_from_attributes = self.select_species_from_optional_attributes(
                tokenization_result.attributes)

            if species_from_attributes is None:
                default_species = default_species
            else:
                default_species = species_from_attributes
            results.extend(self.parse_tokens_to_multiple_candidates(
                tokens=tokens,
                default_species=default_species))
        if len(results) == 0 and "-" in name:
            results = self.parse_multiple_candidates(name.replace("-", " "), default_species=default_species)
            if len(results) == 0 and "GN" in tokenization_result.attributes and "OS" in tokenization_result.attributes:
                # try just parsing the gene name
                return self.parse_multiple_candidates(
                    tokenization_result.attributes["GN"],
                    default_species= tokenization_result.attributes["OS"])
        return self.transform_parse_candidates(results)

    @cache
    def parse(
            self,
            name: str,
            infer_class2_pairing: bool = INFER_CLASS2_PAIRING,
            default_species: Union[Species, str, None] = DEFAULT_SPECIES_PREFIX,
            preferred_result_types: Union[type, Iterable[type], None] = None,
            required_result_types: Union[type, Iterable[type], None] = None,
            only_class1: bool = False,
            only_class2: bool = False,
            max_allele_fields: int = None,
            raise_on_error: bool = True):
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
            If a result of this class is available, return it.

        required_result_types : list of type or None
            If given, only return results with types in this list of classes.

        only_class1 : bool
            Only return results which belong to MHC class I

        only_class2 : bool
            Only return results which belong to MHC class II

        max_allele_fields : int
            If not None, restrict number of allele fields to given value.

        raise_on_error : bool
            If False, return False when parsing is impossible.

        Returns object with one of the following types:
            - Species
            - MhcClass
            - Gene
            - Allele
            - Class2Pair
        """
        candidates = self.parse_multiple_candidates(
            name,
            default_species=default_species)

        if only_class1:
            candidates = [
                candidate for candidate in candidates
                if candidate.is_class1
            ]

        if only_class2:
            candidates = [
                candidate for candidate in candidates
                if candidate.is_class2
            ]

        if required_result_types:
            if type(required_result_types) not in (list, set, tuple):
                required_result_types = [required_result_types]
            candidates = [
                candidate for candidate in candidates
                if type(candidate) in required_result_types
            ]

        if preferred_result_types:
            if type(preferred_result_types) not in (list, set, tuple):
                preferred_result_types = [preferred_result_types]
            candidates_with_preferred_type = [
                candidate for candidate in candidates
                if type(candidate) in preferred_result_types
            ]
            if len(candidates_with_preferred_type) > 0:
                candidates = candidates_with_preferred_type

        if len(candidates) == 0:
            if raise_on_error:
                raise ParseError("Could not parse '%s'" % name)
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