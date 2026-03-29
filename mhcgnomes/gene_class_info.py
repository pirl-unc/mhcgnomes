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

from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


@dataclass(eq=False, repr=False, frozen=True, init=False)
class GeneClassInfo(ResultWithMhcClass):
    """
    Lenient species-aware gene classification result.

    Unlike ``Gene`` or ``Allele``, this object can represent heuristic
    class/chain inference for source-backed gene tokens that are not yet part of
    the strict runtime ontology.
    """

    gene_name: Union[str, None] = None
    chain: Union[str, None] = None
    non_mhc: bool = False
    source: str = ""

    def __init__(
        self,
        species: Species,
        mhc_class: Union[str, None],
        gene_name: Union[str, None] = None,
        chain: Union[str, None] = None,
        non_mhc: bool = False,
        source: str = "",
        raw_string: Union[str, None] = None,
    ):
        ResultWithMhcClass.__init__(
            self, species=species, mhc_class=mhc_class, raw_string=raw_string
        )
        self._set_field(self, "gene_name", gene_name)
        self._set_field(self, "chain", chain)
        self._set_field(self, "non_mhc", bool(non_mhc))
        self._set_field(self, "source", source)

    def to_string(self, include_species=True, use_old_species_prefix=False):
        prefix = ""
        if include_species:
            if use_old_species_prefix:
                prefix = f"{self.species.historic_alias}-"
            else:
                prefix = f"{self.species.prefix}-"

        if self.gene_name:
            return f"{prefix}{self.gene_name}"

        class_bits = []
        if self.mhc_class:
            class_bits.append(f"class {self.mhc_class}")
        if self.chain:
            class_bits.append(self.chain)
        if self.non_mhc and not class_bits:
            class_bits.append("non-MHC")
        label = " ".join(class_bits) if class_bits else "unknown"
        if include_species:
            return f"{self.species.prefix} {label}"
        return label

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )

    def to_record(self):
        record = self.species.to_record()
        if self.gene_name is not None:
            record["gene_name"] = self.gene_name
        if self.mhc_class is not None:
            record["mhc_class"] = self.mhc_class
        if self.chain is not None:
            record["chain"] = self.chain
        record["non_mhc"] = self.non_mhc
        if self.source:
            record["source"] = self.source
        return record
