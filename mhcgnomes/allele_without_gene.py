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

from .species import Species
from .result_with_mhc_class import ResultWithMhcClass

class AlleleWithoutGene(ResultWithMhcClass):
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
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=mhc_class,
            raw_string=raw_string)
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


