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

from .common import unique
from .gene import Gene
from .result_with_species import ResultWithSpecies
from .species import Species


class ResultWithMultipleAlleles(ResultWithSpecies):
    def __init__(
            self,
            species : Species,
            name : str,
            alleles : Sequence[ResultWithSpecies],
            raw_string : Union[str, None] = None):
        ResultWithSpecies.__init__(
            self,
            species=species,
            raw_string=raw_string)
        self.name = name
        self.alleles = tuple(sorted(alleles))

        genes = []
        for allele in self.alleles:
            # monomorphic alleles sometimes represented just by the gene name
            if type(allele) is Gene:
                genes.append(allele)
            elif allele.has_gene:
                genes.append(allele.gene)
        self.genes = unique(genes)
        inferred_species = unique([gene.species for gene in self.genes])

        if len(inferred_species) == 1:
            inferred_species = inferred_species[0]
            if inferred_species != species:
                raise ValueError(
                    "Species inferred from given alleles (%s) is different from %s" % (
                        inferred_species,
                        species,
                    ))
        elif len(inferred_species) > 1:
            raise ValueError(
                "%s '%s' cannot span genes from multiple species: %s" % (
                    self.__class__.__name__,
                    name,
                    inferred_species))

    @classmethod
    def str_field_names(cls):
        return ("species", "name", "num_alleles")

    @classmethod
    def repr_field_names(cls):
        return ("species", "name", "alleles")

    @classmethod
    def eq_field_names(cls):
        return ("species", "name")

    @property
    def num_alleles(self):
        return len(self.alleles)

    @property
    def gene(self):
        if len(self.genes) == 1:
            return list(self.genes)[0]
        else:
            return None

    @property
    def gene_name(self):
        if self.gene:
            return self.gene.name
        else:
            return None

    def collapse_if_possible(self):
        """
        If this serotype contains a single allele, return it.
        """
        if len(self.alleles) == 1:
            return self.alleles[0]
        return None

    @property
    def has_allele(self):
        return len(self.alleles) > 0

    @property
    def is_class1(self):
        return all([allele.is_class1 for allele in self.alleles])

    @property
    def is_class2(self):
        return all([allele.is_class2 for allele in self.alleles])

    @property
    def is_class2_alpha(self):
        return all([allele.is_class2_alpha for allele in self.alleles])

    @property
    def is_class2_beta(self):
        return all([allele.is_class2_beta for allele in self.alleles])

    @property
    def annotation_null(self):
        return any([allele.annotation_null for allele in self.alleles])

    @property
    def annotation_cystosolic(self):
        return any([allele.annotation_cystosolic for allele in self.alleles])

    @property
    def annotation_secreted(self):
        return any([allele.annotation_secreted for allele in self.alleles])

    @property
    def annotation_questionable(self):
        return any([allele.annotation_questionable for allele in self.alleles])

    @property
    def annotation_low_expression(self):
        return any([allele.annotation_low_expression for allele in self.alleles])

    @property
    def annotation_aberrant_expression(self):
        return any([allele.annotation_aberrant_expression for allele in self.alleles])

    @property
    def annotation_group(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return any([allele.annotation_group for allele in self.alleles])

    @property
    def annotation_pseudogene(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return any([allele.annotation_pseudogene for allele in self.alleles])

    @property
    def annotation_splice_variant(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return any([allele.annotation_splice_variant for allele in self.alleles])