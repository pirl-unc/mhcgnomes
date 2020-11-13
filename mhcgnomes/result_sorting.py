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

from typing import List, Iterable

from .allele import Allele
from .allele_without_gene import AlleleWithoutGene
from .class2_pair import Class2Pair
from .haplotype import Haplotype
from .gene import Gene
from .result import Result
from .serotype import Serotype


def pick_best_result(
        candidates: Iterable[Result],
        raise_on_error=True) -> Result:
    if len(candidates) == 0:
        if raise_on_error:
            raise ValueError(
                "Expected at least one candidate ParseResult object")
        else:
            return None
    sorted_candidates = sort_results(candidates)
    return sorted_candidates[0]

def sort_results(results: Iterable[Result]) -> List[Result]:
    if type(results) is not list:
        results = list(results)
    if not results or len(results) == 1:
        return results
    return sorted(results, key=sort_key, reverse=True)


def sort_key(result: Result):
    lower_raw_string = result.raw_string.lower() if result.raw_string else ""
    full_string_matches_raw_string = (
            result.to_string().lower() == lower_raw_string
    )
    compact_string_matches_raw_string = (
            result.compact_string().lower() == lower_raw_string
    )
    if hasattr(result, 'name'):
        name_matches_raw_string = (
                lower_raw_string == result.name.lower())
    else:
        name_matches_raw_string = False
    is_class2_pair = type(result) is Class2Pair
    alpha_is_allele = is_class2_pair and type(result.alpha) is Allele
    alpha_is_valid = (
        is_class2_pair and type(result.alpha) in {Allele, AlleleWithoutGene, Gene}
    )
    beta_is_allele = is_class2_pair and type(result.beta) is Allele
    beta_is_valid = (
        is_class2_pair and type(result.beta) in {Allele, AlleleWithoutGene, Gene}
    )
    is_allele = type(result) is Allele
    is_serotype = type(result) is Serotype
    is_haplotype = type(result) is Haplotype
    is_gene = type(result) is Gene

    if is_allele:
        num_allele_fields = result.num_allele_fields
    elif is_class2_pair and alpha_is_allele and beta_is_allele:
        num_allele_fields = max(
            result.alpha.num_allele_fields,
            result.beta.num_allele_fields)
    else:
        num_allele_fields = 0

    if hasattr(result, 'gene') and result.gene is not None:
        if result.gene.raw_string:
            raw_gene_name_matches_normalized = (
                    result.gene.raw_string.lower() ==
                    result.gene.name.lower()
            )
        else:
            raw_gene_name_matches_normalized = False
        original_gene_seq_length = len(result.gene.raw_string)
    elif is_gene:
        raw_gene_name_matches_normalized = (
                lower_raw_string ==
                result.name.lower()
        )
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
            if not x.isdigit():
                allele_fields_normal = False
                break
            elif all([c == "0" for c in x]):
                allele_fields_normal = False
                break
            elif len(x) < 2 or len(x) > 4:
                allele_fields_normal = False
                break
    else:
        allele_fields_normal = False

    num_alleles_in_haplotype_or_serotype = 0
    if is_serotype or is_haplotype:
        num_alleles_in_haplotype_or_serotype = len(result.alleles)

    return (
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
        is_haplotype,
        num_alleles_in_haplotype_or_serotype,
        result.raw_string is not None,
        # make sure the ordering is stable by sorting on string
        # representation, even if it's semantically meaningful
        str(result),
    )
