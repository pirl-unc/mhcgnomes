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
from collections.abc import Iterable
from typing import Optional

from .allele import Allele
from .allele_without_gene import AlleleWithoutGene
from .class2_locus import Class2Locus
from .gene import Gene
from .haplotype import Haplotype
from .pair import Pair
from .result import Result
from .serotype import Serotype
from .species import Species

# Pattern for serotype names that look like alleles (e.g., B3901, A2403, DR1403)
# These should have lower priority than actual allele interpretations
_ALLELE_LIKE_SEROTYPE_PATTERN = re.compile(r"^([ABC]\d{4,}|D[RPQO][AB]?\d{4,})$")


def species_ontology_depth(result: Result) -> int:
    """
    How deep the result's species sits in the ontology, i.e. how specific a
    claim it makes about the species.

    A species prefix is inherited by descendants, so a bare prefix matches an
    ancestor and every species under it -- "BoLA" matches both Bos sp. and
    Bubalus bubalis, "RT1" matches Rattus sp. and every Rattus species. In that
    situation the input gave no evidence for the more specific species, so the
    ancestor is the honest reading and the descendants are guesses.
    """
    species = result if type(result) is Species else getattr(result, "species", None)
    depth = 0
    while species is not None and species.parent_species is not None:
        species = species.parent_species
        depth += 1
    return depth


def pick_best_result(candidates: Iterable[Result], raise_on_error=True) -> Optional[Result]:
    if len(candidates) == 0:
        if raise_on_error:
            raise ValueError("Expected at least one candidate ParseResult object")
        else:
            return None
    sorted_candidates = sort_results(candidates)
    return sorted_candidates[0]


def sort_results(results: Iterable[Result]) -> list[Result]:
    if type(results) is not list:
        results = list(results)
    if not results or len(results) == 1:
        return results
    return sorted(results, key=sort_key, reverse=True)


def sort_key(result: Result):
    lower_raw_string = result.raw_string.lower() if result.raw_string else ""
    full_string_matches_raw_string = result.to_string().lower() == lower_raw_string
    compact_string_matches_raw_string = result.compact_string().lower() == lower_raw_string
    if hasattr(result, "name"):
        name_matches_raw_string = lower_raw_string == result.name.lower()
    else:
        name_matches_raw_string = False
    t = type(result)
    is_class2_pair = t is Pair
    alpha_is_allele = is_class2_pair and type(result.alpha) is Allele
    alpha_is_valid = is_class2_pair and type(result.alpha) in {Allele, AlleleWithoutGene, Gene}
    beta_is_allele = is_class2_pair and type(result.beta) is Allele
    beta_is_valid = is_class2_pair and type(result.beta) in {Allele, AlleleWithoutGene, Gene}
    is_allele = t is Allele
    is_allele_without_gene = t is AlleleWithoutGene
    is_serotype = t is Serotype
    is_haplotype = t is Haplotype
    is_class2_locus = t is Class2Locus
    is_gene = t is Gene

    # Penalize serotypes that look like alleles (e.g., B3901, A2403)
    # These should have lower priority than actual allele interpretations
    is_allele_like_serotype = is_serotype and bool(_ALLELE_LIKE_SEROTYPE_PATTERN.match(result.name))

    if is_allele:
        num_allele_fields = result.num_allele_fields
    elif is_class2_pair and alpha_is_allele and beta_is_allele:
        num_allele_fields = max(result.alpha.num_allele_fields, result.beta.num_allele_fields)
    else:
        num_allele_fields = 0

    if hasattr(result, "gene") and result.gene is not None:
        if result.gene.raw_string:
            raw_gene_name_matches_normalized = (
                result.gene.raw_string.lower() == result.gene.name.lower()
            )
        else:
            raw_gene_name_matches_normalized = False
        original_gene_seq_length = len(result.gene.raw_string)
    elif is_gene:
        raw_gene_name_matches_normalized = lower_raw_string == result.name.lower()
        original_gene_seq_length = len(result.raw_string)
    else:
        raw_gene_name_matches_normalized = False
        original_gene_seq_length = 0

    if is_allele:
        allele_fields = result.allele_fields
    elif is_class2_pair and alpha_is_allele and beta_is_allele:
        allele_fields = result.alpha.allele_fields + result.beta.allele_fields
    else:
        allele_fields = ()

    if len(allele_fields) > 0:
        allele_fields_normal = True
        for x in allele_fields:
            if not x.isdigit() or all(c == "0" for c in x) or len(x) < 2 or len(x) > 4:
                allele_fields_normal = False
                break
    else:
        allele_fields_normal = False

    num_alleles_in_haplotype_or_serotype = 0
    if is_serotype or is_haplotype:
        num_alleles_in_haplotype_or_serotype = len(result.alleles)

    return (
        # Penalize serotypes that look like alleles (B3901, A2403, etc.)
        # These should be lower priority than allele interpretations
        not is_allele_like_serotype,
        name_matches_raw_string,
        allele_fields_normal,
        # for Class II pairs, prefer Allele objects for alpha and beta
        # and then any of {AlleleWpithoutGene, Allele, Gene} where
        # genes play the role of mono-morphic alleles
        (is_class2_pair and alpha_is_allele and beta_is_allele),
        (is_class2_pair and alpha_is_valid and beta_is_valid),
        is_allele,
        full_string_matches_raw_string,
        compact_string_matches_raw_string,
        is_gene,
        raw_gene_name_matches_normalized,
        num_allele_fields,
        original_gene_seq_length,
        is_serotype,
        # Haplotypes with defined alleles (e.g. H2-a with 9 alleles) outrank
        # Class II loci, but Class II loci outrank empty haplotypes
        # (e.g. RT1-B as Class2Locus beats RT1-b as Haplotype with 0 alleles)
        (is_haplotype and num_alleles_in_haplotype_or_serotype > 0),
        is_class2_locus,
        is_haplotype,
        is_allele_without_gene,
        num_alleles_in_haplotype_or_serotype,
        result.raw_string is not None,
        # When results are otherwise indistinguishable and differ only in which
        # species they name, prefer the least specific one. This only matters
        # when a single string matched an ancestor and its descendants, in
        # which case nothing in the input justified picking a descendant.
        -species_ontology_depth(result),
        # make sure the ordering is stable by sorting on string
        # representation, even if it's semantically meaningful
        str(result),
    )
