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

from collections.abc import Sequence
from typing import Optional, Union

from .gene import Gene
from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


class Class2Locus(ResultWithMhcClass):
    """
    Represents an MHC Class II locus (e.g., DR, DQ, DP).

    A Class II locus groups together the alpha and beta chain genes for a
    specific Class II molecule. For example, "HLA-DR" includes DRA (alpha)
    and DRB1, DRB3, DRB4, DRB5 (beta) genes.

    Parameters
    ----------
    species : Species
        The species this locus belongs to.
    name : str
        The locus name (e.g., "DR", "DQ", "DP").
    mhc_class : str, default "II"
        The MHC class (always "II" for Class2Locus).
    genes : Sequence[Gene], optional
        The genes belonging to this locus.
    raw_string : str, optional
        The original unparsed string.

    Attributes
    ----------
    species : Species
        The species this locus belongs to.
    name : str
        The locus name.
    genes : list of Gene
        The genes in this locus.
    alpha_chain_genes : list of Gene
        Alpha chain genes (names ending in "A").
    beta_chain_genes : list of Gene
        Beta chain genes (names ending in "B").

    Examples
    --------
    >>> from mhcgnomes import Class2Locus
    >>> locus = Class2Locus.get("HLA", "DR")
    >>> locus.name
    'DR'
    >>> locus.alpha_chain_gene_names
    ['DRA']
    """
    def __init__(
            self,
            species : Species,
            name : str,
            mhc_class : str = "II",
            genes : Optional[Sequence[Gene]] = None,
            raw_string : Union[str, None] = None):
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=mhc_class,
            raw_string=raw_string)
        self.name = name
        self.genes = genes if genes is not None else []

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
        while s1 and s1[-1].isdigit():
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
