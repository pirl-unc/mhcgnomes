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
from typing import Union

from .allele import Allele
from .result_with_multiple_alleles import ResultWithMultipleAlleles
from .species import Species


class Serotype(ResultWithMultipleAlleles):
    """
    Represents an MHC serotype (serological antigen type).

    A Serotype represents a group of MHC alleles that are recognized by the
    same antibody. For example, "HLA-A2" is a serotype that includes multiple
    alleles like A*02:01, A*02:02, etc.

    Serotypes are commonly used in older literature and transplantation
    medicine before high-resolution molecular typing became available.

    Parameters
    ----------
    species : Species
        The species this serotype belongs to.
    name : str
        The serotype name (e.g., "A2", "B27", "DR4").
    alleles : Sequence[Allele]
        The alleles that belong to this serotype.
    raw_string : str, optional
        The original unparsed string.

    Attributes
    ----------
    species : Species
        The species this serotype belongs to.
    name : str
        The serotype name.
    alleles : Sequence[Allele]
        The alleles in this serotype.

    Examples
    --------
    >>> from mhcgnomes import parse
    >>> sero = parse("HLA-A2")
    >>> sero.name
    'A2'
    >>> len(sero.alleles) > 0
    True
    """

    def __init__(
        self,
        species: Species,
        name: str,
        alleles: Sequence[Allele],
        raw_string: Union[str, None] = None,
    ):
        ResultWithMultipleAlleles.__init__(
            self, species=species, name=name, alleles=alleles, raw_string=raw_string
        )

    def to_string(self, include_species=True, use_old_species_prefix=False):
        if include_species:
            return f"{self.species.to_string(use_old_species_prefix=use_old_species_prefix)}-{self.name}"
        else:
            return self.name

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )

    def to_record(self):
        d = self.species.to_record()
        d["serotype"] = self.to_string()
        return d
