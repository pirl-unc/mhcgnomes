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

from typing import Union
from collections import OrderedDict

from .allele import Allele
from .allele_without_gene import AlleleWithoutGene
from .gene import Gene
from .result_with_mhc_class import ResultWithMhcClass


class Class2Pair(ResultWithMhcClass):
    """
    Representation of an alpha/beta pair of Class II MHC chains.
    """

    def __init__(
            self,
            alpha : Union[Allele, AlleleWithoutGene, Gene],
            beta : Union[Allele, AlleleWithoutGene, Gene],
            mhc_class="II",
            raw_string : Union[str, None] = None):
        ResultWithMhcClass.__init__(
            self,
            species=alpha.species,
            mhc_class=mhc_class,
            raw_string=raw_string)
        self.alpha = alpha
        self.beta = beta

    @classmethod
    def hash_field_names(cls):
        return ("alpha", "beta")

    @classmethod
    def eq_field_names(cls):
        return ("alpha", "beta")

    @classmethod
    def get(cls, alpha, beta, raw_string=None):
        if alpha is None:
            return None
        if beta is None:
            return None
        if not isinstance(alpha, (Allele, Gene, AlleleWithoutGene)):
            return None
        if not isinstance(beta, (Allele, Gene, AlleleWithoutGene)):
            return None
        if alpha.mhc_class == beta.mhc_class:
            mhc_class = alpha.mhc_class
        else:
            mhc_class = "II"

        return cls(
            alpha=alpha,
            beta=beta,
            mhc_class=mhc_class,
            raw_string=raw_string)

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False):
        return "%s-%s" % (
            self.alpha.to_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix),
            self.beta.to_string(
                include_species=False))

    def compact_string(
            self,
            include_species=False,
            use_old_species_prefix=False):
        return "%s-%s" % (
            self.alpha.compact_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix),
            self.beta.compact_string(include_species=False))

    @property
    def gene_name(self):
        return "%s/%s" % (self.alpha.gene_name, self.beta.gene_name)

    def to_record(self):
        # return a dictionary that has the same elements as Gene.to_dict()
        # along with "allele"
        return OrderedDict([
            ("gene", self.gene_name),
            ("mhc_class", self.mhc_class),
            ("is_mutant", False),
            ("allele", self.to_string()),
        ])

    def restrict_num_allele_fields(
            self,
            num_fields: int,
            drop_annotations: bool = False,
            drop_mutations: bool = False):
        if type(self.alpha) is Allele:
            alpha = self.alpha.restrict_num_allele_fields(
                num_fields=num_fields,
                drop_annotations=drop_annotations,
                drop_mutations=drop_mutations)
        else:
            alpha = self.alpha
        if type(self.beta) is Allele:
            beta = self.beta.restrict_num_allele_fields(
                num_fields=num_fields,
                drop_annotations=drop_annotations,
                drop_mutations=drop_mutations)
        else:
            beta = self.beta
        if alpha != self.alpha or beta != self.beta:
            return Class2Pair.get(alpha=alpha, beta=beta, raw_string=self.raw_string)
        else:
            return self

    @property
    def annotation_null(self):
        return (
            self.alpha.annotation_null or
            self.beta.annotation_null)

    @property
    def annotation_cystosolic(self):
        return (
            self.alpha.annotation_cystosolic or
            self.beta.annotation_cystosolic)

    @property
    def annotation_secreted(self):
        return (
            self.alpha.annotation_secreted or
            self.beta.annotation_secreted)

    @property
    def annotation_questionable(self):
        return (
            self.alpha.annotation_questionable or
            self.beta.annotation_questionable)

    @property
    def annotation_low_expression(self):
        return (
            self.alpha.annotation_low_expression or
            self.beta.annotation_low_expression)

    @property
    def annotation_aberrant_expression(self):
        return (
            self.alpha.annotation_aberrant_expression or
            self.beta.annotation_aberrant_expression)

    @property
    def annotation_group(self):
        return (
            self.alpha.annotation_group or
            self.beta.annotation_group)

    @property
    def annotation_pseudogene(self):
        return (
            self.alpha.annotation_pseudogene or
            self.beta.annotation_pseudogene)

    @property
    def annotation_splice_variant(self):
        return (
            self.alpha.annotation_splice_variant or
            self.beta.annotation_splice_variant)


default_human_alpha_chains = {
    # The DR alpha chain is effectively constant across the population
    "DRB": Allele.get("HLA", "DRA", "01", "01"),
    # Most common alpha chain for DP is DPA*01:03 but we really
    # need to change this logic to use a lookup table of pairwise
    # frequencies for inferring the alpha-beta pairing
    "DPB": Allele.get("HLA", "DPA1", "01", "03"),
    # Most common DQ alpha (according to wikipedia) is DQA1*01:02
    # but like DPA we should use pair frequencies in the future
    "DQB": Allele.get("HLA", "DQA1", "01", "02")
}


def infer_class2_alpha_chain(beta):
    """
    Given an Allele for a Class II beta chain, returns the alpha/beta pair with
    a population invariant alpha chain (if one is known)
    """
    if isinstance(beta, Class2Pair):
        return beta

    if not isinstance(beta, Allele):
        return beta

    if not beta.is_class2:
        return beta

    if beta.species_prefix != "HLA":
        return beta

    locus = beta.gene_name[:3]
    if locus not in default_human_alpha_chains:
        return beta

    alpha = default_human_alpha_chains.get(locus)

    if alpha is None:
        return beta

    return Class2Pair.get(alpha, beta)
