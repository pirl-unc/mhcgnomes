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
from .result_with_multiple_alleles import ResultWithMultipleAlleles
from .species import Species


class Serotype(ResultWithMultipleAlleles):
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
        ResultWithMultipleAlleles.__init__(
            self,
            species=species,
            name=name,
            alleles=alleles,
            raw_string=raw_string)

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
