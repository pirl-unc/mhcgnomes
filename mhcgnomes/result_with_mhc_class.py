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

from dataclasses import dataclass
from typing import Union

from .mhc_class_helpers import is_class1, is_class2
from .result_with_species import ResultWithSpecies


@dataclass(eq=False, repr=False, frozen=True, init=False)
class ResultWithMhcClass(ResultWithSpecies):
    """
    Common base class for any result object which has a species field.

    Useful for sharing helper methods that rely on the 'species' field.
    """

    mhc_class: Union[str, None] = None

    def __init__(self, species, mhc_class, raw_string=None):
        ResultWithSpecies.__init__(self, species=species, raw_string=raw_string)
        self._set_field(self, "mhc_class", mhc_class)

    @property
    def has_mhc_class(self):
        return True

    @property
    def is_class1(self):
        return is_class1(self.mhc_class)

    @property
    def is_class2(self):
        return is_class2(self.mhc_class)

    @property
    def class2_chain_type(self):
        """
        "alpha", "beta", or None for anything that does not name one gene.

        Lives here rather than on ResultWithGene so that Gene gets it too.
        Gene is a sibling of ResultWithGene rather than a subclass, so before
        this it fell through to Result's `return False` stubs and every class II
        gene reported neither chain -- which also made "HLA-DRA alpha"
        unparseable, since the parser gates chain-suffixed candidates on these
        predicates while listing Gene among the candidate types. See #137.

        Pair has no single gene name and correctly answers None.
        """
        gene_name = getattr(self, "gene_name", None)
        if not self.is_class2 or not gene_name:
            return None
        # .get rather than [] : a class II gene with no curated chain type is
        # unknown, not a crash. None today, but the ontology grows.
        return self.species.class2_gene_name_to_chain_type.get(gene_name)

    @property
    def is_class2_alpha(self):
        return self.class2_chain_type == "alpha"

    @property
    def is_class2_beta(self):
        return self.class2_chain_type == "beta"
