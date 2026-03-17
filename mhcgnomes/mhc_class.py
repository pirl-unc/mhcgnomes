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

from .errors import ParseError
from .gene import Gene
from .mhc_class_helpers import (
    is_class1,
    is_class2,
    is_valid_restriction,
    normalize_mhc_class_string,
)
from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


@dataclass(eq=False, repr=False, frozen=True, init=False)
class MhcClass(ResultWithMhcClass):
    """
    Wrapper class for species combined with MHC classes such as
    "I", "Ia", "Ib", "II", "IIa", &c
    which provides some utility functions.

    Optionally includes a chain restriction ("alpha" or "beta") for
    cases like MHCIIB (class II beta, unknown locus).
    """

    chain: Union[str, None] = None

    def __init__(
        self,
        species: Species,
        mhc_class: str,
        chain: Union[str, None] = None,
        raw_string: Union[str, None] = None,
    ):
        ResultWithMhcClass.__init__(
            self, species=species, mhc_class=mhc_class, raw_string=raw_string
        )
        object.__setattr__(self, "chain", chain)

    @classmethod
    def get(cls, species_prefix, mhc_class, chain=None):
        species = Species.get(species_prefix)
        if species is None:
            return None
        try:
            mhc_class = normalize_mhc_class_string(mhc_class)
        except ParseError:
            return None
        return MhcClass(species, mhc_class, chain=chain)

    @property
    def is_class1(self):
        return is_class1(self.mhc_class)

    @property
    def is_class2(self):
        return is_class2(self.mhc_class)

    def genes(self):
        """
        Returns all gene names whose MHC class matches this MHC class
        """
        return [
            Gene.get(self.species, gene_name)
            for gene_name in sorted(self.species.gene_names)
            if is_valid_restriction(self.mhc_class, self.species.get_mhc_class_of_gene(gene_name))
        ]

    def to_record(self):
        d = self.species.to_record()
        d["mhc_class"] = self.mhc_class
        if self.chain is not None:
            d["chain"] = self.chain
        return d

    def to_string(self, include_species=True, use_old_species_prefix=False):
        if include_species:
            if self.common_species_name:
                species_str = self.common_species_name.lower()
            elif use_old_species_prefix:
                species_str = self.species.historic_alias
            else:
                species_str = self.species.prefix
            prefix = f"{species_str} "
        else:
            prefix = ""
        class_str = f"class {self.mhc_class}"
        if self.chain is not None:
            class_str = f"{class_str} {self.chain}"
        return f"{prefix}{class_str}"

    def compact_string(self, include_species=True, use_old_species_prefix=False):
        """
        Compact representation of an MHC class, currently same as the
        normalized representation.
        """
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )
