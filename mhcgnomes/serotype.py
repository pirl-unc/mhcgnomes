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
from .result_with_species import ResultWithSpecies
from .species import Species


class Serotype(ResultWithSpecies):
    """
    Common base class for all result objects which have a species field.

    Contains many common helpers such as `is_human`.
    """
    def __init__(
            self,
            species : Species,
            name : str,
            alleles : Sequence[Allele],
            raw_string : Union[str, None] = None):
        ResultWithSpecies.__init__(
            self,
            species=species,
            raw_string=raw_string)
        self.name = name
        self.alleles = tuple(sorted(alleles))

        self.genes = list({allele.gene for allele in alleles})

        inferred_species = {
            gene.species for gene in self.genes
        }
        if len(inferred_species) == 1:
            inferred_species = list(inferred_species)[0]
            if inferred_species != species:
                raise ValueError(
                    "Species inferred from given alleles (%s) is different from %s" % (
                        inferred_species,
                        species,
                    ))
        elif len(inferred_species) > 1:
            raise ValueError(
                "Serotype '%s' cannot span genes from multiple species: %s" % (
                    name,
                    inferred_species,
                ))

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

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False):
        if include_species:
            return "%s-%s" % (
                self.species.to_string(
                    use_old_species_prefix=use_old_species_prefix),
                self.name)
        else:
            return self.name


    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)

    def to_record(self):
        d = self.species.to_record()
        d["serotype"] = self.to_string()
        return d

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
