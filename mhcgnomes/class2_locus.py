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

from typing import Union, Sequence

from .result_with_mhc_class import ResultWithMhcClass
from .species import Species
from .gene import Gene

class Class2Locus(ResultWithMhcClass):
    def __init__(
            self,
            species : Species,
            name : str,
            mhc_class : str = "II",
            genes : Sequence[Gene] = [],
            raw_string : Union[str, None] = None):
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=mhc_class,
            raw_string=raw_string)
        self.name = name
        self.genes = genes

    @property
    def locus_name(self):
        return self.name

    @classmethod
    def eq_field_names(cls):
        return ("species", "name")

    @classmethod
    def str_field_names(cls):
        return ("species", "name")

    def to_string(self, include_species=True, use_old_species_prefix=False):
        species_string = self.species.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)
        return species_string + "-" + self.name

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)

    @property
    def gene_names(self):
        return [g.name for g in self.genes]

    @classmethod
    def endswith_ignore_digits(cls, s1, s2):
        while s1[-1].isdigit():
            s1 = s1[:-1]
        return s1.endswith(s2)

    @property
    def alpha_chain_genes(self):
        results = []
        for g in self.genes:
            name = g.name
            if self.endswith_ignore_digits(name.lower(), "a"):
                results.append(g)
        return results


    @property
    def beta_chain_genes(self):
        results = []
        for g in self.genes:
            name = g.name
            if self.endswith_ignore_digits(name.lower(), "b"):
                results.append(g)
        return results

    @property
    def alpha_chain_gene_names(self):
        return [g.name for g in self.alpha_chain_genes]

    @property
    def beta_chain_gene_names(self):
        return [g.name for g in self.beta_chain_genes]

    @classmethod
    def get(cls, species_prefix, locus_name):
        if type(species_prefix) is Species:
            species = species_prefix
        else:
            species = Species.get(species_prefix)
            if species is None:
                return None

        raw_string = locus_name
        locus_name = species.find_matching_class2_locus_name(locus_name)
        if locus_name is None:
            return None

        gene_names = species.class2_locus_to_gene_names[locus_name]
        genes = []
        for gene_name in gene_names:
            gene = Gene.get(species, gene_name)
            if gene is None:
                continue
            genes.append(gene)
        return Class2Locus(
            species=species,
            name=locus_name,
            genes=genes,
            raw_string=raw_string)
