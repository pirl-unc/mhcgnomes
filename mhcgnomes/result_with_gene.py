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

from .result_with_mhc_class import ResultWithMhcClass

class ResultWithGene(ResultWithMhcClass):
    """
    Common base class for any result object which has a species field.

    Useful for sharing helper methods that rely on the 'species' field.
    """
    def __init__(self, gene, raw_string=None):
        ResultWithMhcClass.__init__(
            self,
            species=gene.species,
            mhc_class=gene.mhc_class,
            raw_string=raw_string)
        self.gene = gene

    @property
    def has_gene(self):
        return True

    @property
    def gene_name(self):
        return self.gene.name


    @property
    def is_class2_alpha(self):
        return (
            self.is_class2 and
            self.species.class2_gene_name_to_chain_type[self.gene_name] == "alpha")

    @property
    def is_class2_beta(self):
        return (
            self.is_class2 and
            self.species.class2_gene_name_to_chain_type[self.gene_name] == "beta")