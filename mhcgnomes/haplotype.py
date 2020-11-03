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

from typing import Sequence, Union

from .allele import Allele
from .mhc_class_helpers import (
    is_valid_restriction,
    restrict_alleles,
)
from .class2_locus import Class2Locus
from .class2_pair import Class2Pair
from .result_with_multiple_alleles  import ResultWithMultipleAlleles
from .species import Species

class Haplotype(ResultWithMultipleAlleles):
    def __init__(
            self,
            species : Species,
            name : str,
            alleles : Sequence[Allele],
            class_restriction : Union[str, None] = None,
            locus_restriction : Union[Class2Locus, None] = None,
            parent_haplotypes : Union[Sequence["Haplotype"], None] = None,
            raw_string : Union[str, None] = None):
        ResultWithMultipleAlleles.__init__(
            self,
            species=species,
            name=name,
            alleles=alleles,
            raw_string=raw_string)
        self.class_restriction = class_restriction
        self.locus_restriction = locus_restriction
        self.parent_haplotypes = parent_haplotypes

    @classmethod
    def str_field_names(cls):
        return (
            "species",
            "name",
            "num_alleles",
            "class_restriction",
            "locus_restriction"
        )

    @classmethod
    def repr_field_names(cls):
        return (
            "species",
            "name",
            "alleles",
            "class_restriction",
            "locus_restriction"
        )

    @classmethod
    def eq_field_names(cls):
        return (
            "species",
            "name",
            "class_restriction",
            "locus_restriction"
        )

    @property
    def haplotype_name(self):
        return self.name

    def restrict_mhc_class(self, class_restriction, raise_on_error=True):
        if class_restriction is None:
            return self
        if self.class_restriction == class_restriction:
            return self
        if not is_valid_restriction(self.class_restriction, class_restriction):
            if raise_on_error:
                raise ValueError(
                    "Cannot restrict '%s' to class '%s'" % (
                        self.to_string(),
                        class_restriction))
            else:
                return None
        restricted_alleles = restrict_alleles(self.alleles, class_restriction)
        return Haplotype(
            species=self.species,
            name=self.name,
            alleles=restricted_alleles,
            class_restriction=class_restriction,
            locus_restriction=self.locus_restriction,
            raw_string=self.raw_string)

    def restrict_class2_locus(self, class2_locus : Class2Locus, raise_on_error=True):
        if class2_locus is None:
            return self
        if self.locus_restriction == class2_locus:
            return self
        if self.locus_restriction is not None:
            if raise_on_error:
                raise ValueError(
                    "Haplotype %s already has locus restriction, cannot restrict to %s" % (
                        self, class2_locus))
            else:
                return None
        valid_genes = set(class2_locus.genes)

        restricted_alleles = [
            allele
            for allele in self.alleles
            if allele.gene in valid_genes
        ]
        return Haplotype(
            species=self.species,
            name=self.name,
            alleles=restricted_alleles,
            class_restriction=self.class_restriction,
            locus_restriction=class2_locus,
            raw_string=self.raw_string)

    def collapse_if_possible(self):
        """
        If this haplotype contains a single allele or a single pair of
        class alleles for the same locus, return it. Otherwise return None.
        """
        allele = self.get_single_allele()
        if allele:
            return allele

        class2_pair = self.get_class2_pair()
        if class2_pair:
            return class2_pair
        return None

    def get_single_allele(self):
        if len(self.alleles) == 1:
            return self.alleles[0]
        return None

    def get_class2_pair(self):
        if self.locus_restriction is None:
            return None
        alpha_genes = self.locus_restriction.alpha_chain_genes
        beta_genes = self.locus_restriction.beta_chain_genes

        if len(alpha_genes) == 0 or len(beta_genes) == 0:
            return None
        alpha_alleles = [
            a for a in self.alleles
            if a.gene in alpha_genes
        ]
        beta_alleles = [
            a for a in self.alleles
            if a.gene in beta_genes
        ]
        if len(alpha_alleles) != 1 or len(beta_alleles) != 1:
            return None

        alpha = alpha_alleles[0]
        beta = beta_alleles[0]
        return Class2Pair(alpha, beta)

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False):
        if self.locus_restriction:
            result = self.locus_restriction.to_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix)
        else:
            result = self.species.to_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix)

        result += ("-%s" % (self.name,))

        if self.class_restriction:
            result += " class %s" % (self.class_restriction,)

        return result

    def compact_string(self, include_species=False):
        return self.to_string(include_species=include_species)
