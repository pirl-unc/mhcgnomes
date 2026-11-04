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

from .result_with_mhc_class import ResultWithMhcClass
from .species import Species


@dataclass(eq=False, repr=False, frozen=True, init=False)
class AlleleWithoutGene(ResultWithMhcClass):
    """
    Written allele or molecule designation without an established ontology gene.

    Includes unstructured names and source-backed registry designations whose
    locus is not established in this ontology. Parsing does not validate a molecule.
    """

    name: str = ""

    def __init__(
        self,
        species: Species,
        name: str,
        mhc_class: str | None = None,
        raw_string: str | None = None,
    ):
        ResultWithMhcClass.__init__(
            self, species=species, mhc_class=mhc_class, raw_string=raw_string
        )
        self._set_field(self, "name", name)

    def to_string(self, include_species=True, use_old_species_prefix=False):
        """
        Return allele strings like "BoLA-T2C"
        """
        species_str = self.species.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )
        if species_str:
            return f"{species_str}-{self.name}"
        return self.name

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        """
        Compact representation, e.g. just "T2C" instead of "BoLA-T2C"
        """
        return self.name

    @property
    def registry_identities(self):
        """Identities for an exact designation without an established ontology gene."""
        from .registry_identity import get_registry_identities

        name = f"{self.species.canonical_mhc_prefix}-{self.name}"
        return get_registry_identities(name, include_aliases=False)

    def restrict_allele_fields(self, num_fields):
        """Truncate written gene*field names; leave unstructured identifiers unchanged.

        A truncated name no longer carries the full accession identity. This
        operation does not establish the unknown gene or a registry allele.
        """
        locus, separator, fields = self.name.partition("*")
        if not separator or len(fields.split(":")) <= num_fields:
            return self
        return self.copy(name=f"{locus}*{':'.join(fields.split(':')[:num_fields])}")

    def to_record(self):
        """Serialize the species, written designation, class and optional registry identity."""
        record = self.species.to_record()
        record.update(allele=self.to_string(), mhc_class=self.mhc_class)
        if self.registry_identity is not None:
            record.update(self.registry_identity.to_record())
        return record

    @classmethod
    def get(cls, species, name, mhc_class=None, raw_string=None):
        species = Species.get(species)
        if not species:
            return None

        if not name:
            return None

        return cls(species=species, name=name, mhc_class=mhc_class, raw_string=raw_string)
