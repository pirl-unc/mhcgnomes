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

from typing import Union


from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


class Gene(ResultWithMhcClass):
    def __init__(
            self,
            species : Species,
            name : str,
            raw_string : Union[str, None] = None):
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=species.get_mhc_class_of_gene(name),
            raw_string=raw_string)
        self.name = name

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
    def get(cls, species_prefix : Union[str, Species], gene_name : str):
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
            raw_string=raw_string)

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
            return "%s-%s" % (species_str, self.gene_name)
        else:
            return self.gene_name

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
        return d
