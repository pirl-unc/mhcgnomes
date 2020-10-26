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
from .result_with_species import ResultWithSpecies

class Class2Pair(ResultWithSpecies):
    """
    Representation of an alpha/beta pair of Class II MHC chains.
    """

    def __init__(
            self,
            alpha : Allele,
            beta : Allele,
            raw_string : Union[str, None] = None):
        ResultWithSpecies.__init__(
            self,
            species=alpha.species,
            raw_string=raw_string)
        self.alpha = alpha
        self.beta = beta

    @property
    def is_class1(self):
        return False

    @property
    def is_class2(self):
        return True

    @classmethod
    def get(cls, alpha, beta, raw_string=None):
        if alpha is None:
            return None
        if beta is None:
            return None
        return cls(alpha=alpha, beta=beta, raw_string=raw_string)

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
    def mhc_class(self):
        alpha_class = self.alpha.mhc_class
        if alpha_class:
            return alpha_class
        else:
            return self.beta.mhc_class

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

    return Class2Pair(alpha, beta)
