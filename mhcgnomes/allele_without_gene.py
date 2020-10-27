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

from typing import List, Tuple, Union

from .mhc_class_helpers import is_class1, is_class2
from .species import Species
from .result_with_species import ResultWithSpecies

class AlleleWithoutGene(ResultWithSpecies):
    """
    Identifier for molecule whose gene is unknown and no proper allele numbering
    is given for.
    """
    def __init__(
            self,
            species : Species,
            name : str,
            mhc_class : Union[str, None] = None,
            raw_string : Union[str, None] = None):
        ResultWithSpecies.__init__(self, species=species, raw_string=raw_string)
        self.mhc_class = mhc_class
        self.name = name

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False):
        """
        Return allele strings like "BoLA-T2C"
        """
        species_str = self.species_str.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)
        return "%s-%s" % (species_str, self.name)

    def compact_string(
            self,
            include_species=False,
            use_old_species_prefix=False):
        """
        Compact representation, e.g. just "T2C" instead of "BoLA-T2C"
        """
        return self.name

    @classmethod
    def get(cls, species, name, raw_string=None):
        species = Species.get(species)
        if not species:
            return None

        if not name:
            return None

        return cls(
            species=species,
            name=name,
            raw_string=raw_string)

    @property
    def is_class1(self):
        return self.mhc_class and is_class1(self.mhc_class)

    @property
    def is_class2(self):
        return self.mhc_class and is_class2(self.mhc_class)

    @property
    def annotation_null(self):
        return False

    @property
    def annotation_cystosolic(self):
        return False

    @property
    def annotation_secreted(self):
        return False

    @property
    def annotation_questionable(self):
        return False

    @property
    def annotation_low_expression(self):
        return False

    @property
    def annotation_aberrant_expression(self):
        return False

    @property
    def annotation_group(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False

    @property
    def annotation_pseudogene(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False

    @property
    def annotation_splice_variant(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False