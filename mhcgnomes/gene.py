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

from __future__ import print_function, division, absolute_import

from typing import Union, Iterable

from .mutation import Mutation
from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


class Gene(ResultWithMhcClass):
    def __init__(
            self,
            species: Species,
            name: str,
            mutations: Iterable[Mutation] = (),
            raw_string: Union[str, None] = None):
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=species.get_mhc_class_of_gene(name),
            raw_string=raw_string)
        self.name = name
        self.mutations = mutations

    def __hash__(self):
        return hash((self.species, self.name, self.mutations))

    def __eq__(self, other):
        if type(other) is not Gene:
            return False
        return (
            self.species == other.species and
            self.name == other.name and
            self.mutations == other.mutations
        )

    @property
    def raw_string_was_alias(self):
        return self.raw_string in self.species.gene_aliases

    @property
    def gene_name(self):
        return self.name

    @property
    def gene(self):
        return self

    @classmethod
    def get(cls, species_prefix: Union[str, Species], gene_name: str, mutations: Iterable[Mutation] = ()):
        """
        Returns Gene if gene name is in ontology, otherwise None
        """
        # use the canonical gene name e.g. "A" and not "a"
        if type(species_prefix) is Species:
            species = species_prefix
        else:
            species = Species.get(species_prefix)
        if species is None:
            return None

        raw_string = gene_name

        gene_name = species.find_matching_gene_name(gene_name)

        if gene_name is None:
            return None

        return Gene(
            species,
            gene_name,
            mutations=mutations,
            raw_string=raw_string)

    def copy_without_mutations(self):
        return self.copy(mutations=())

    def copy_with_extra_mutations(self, mutations: Iterable[Mutation]):
        return self.copy(mutations=self.mutations + tuple(mutations))

    def mutation_string(self):
        return " ".join([mut.to_string() for mut in self.mutations])

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False):
        if include_species:
            # non-classical genes located outside the MHC locus
            # get identified with the common species name if possible
            if self.mhc_class in {"Id"}:
                species_str = self.common_species_name
            elif use_old_species_prefix:
                species_str = self.species.historic_mhc_prefix
            else:
                species_str = self.species_prefix
            result = "%s-%s" % (species_str, self.gene_name)
        else:
            result = self.gene_name
        if self.is_mutant:
            result += " %s mutant" % self.mutation_string()
        return result

    def compact_string(
            self,
            include_species=False,
            use_old_species_prefix=False):
        """
        Compact representation of a Locus, currently same as the
        normalized representation.
        """
        return Gene.to_string(
            self,
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)

    @property
    def is_mutant(self):
        return len(self.mutations) > 0


    def to_record(self):
        """
        Returns a user-viewable ordered dictionary with a representation  of
        this gene, and the values of the following methods:
            - is_mutant
            - get_mhc_class
        """
        d = self.species.to_record()
        d["gene"] = self.to_string()
        d["mhc_class"] = self.mhc_class
        d["mutations"] = self.mutation_string()
        d["is_mutant"] = self.is_mutant
        return d

    def restrict_allele_fields(
            self,
            num_fields,
            drop_annotations=False,
            drop_mutations=False):
        return self.copy(mutations=[] if drop_mutations else self.mutations)
