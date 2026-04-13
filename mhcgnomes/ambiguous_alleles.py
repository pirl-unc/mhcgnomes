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
from dataclasses import dataclass
from typing import Union

from .result_with_multiple_alleles import ResultWithMultipleAlleles
from .result_with_species import ResultWithSpecies
from .species import Species


@dataclass(eq=False, repr=False, frozen=True, init=False)
class AmbiguousAlleles(ResultWithMultipleAlleles):
    """
    A set of distinct allele designations that an input string cannot
    disambiguate between. Used for IPD-MHC style slash designations
    such as "SahaI*74/88" (Caldwell et al. 2018, PMC6092122), where an
    observed sequence matches two database entries because they are
    identical in the region that was typed.

    Unlike Serotype or Haplotype, the grouping here does not reflect a
    biological or serological relationship — just typing ambiguity.
    """

    def __init__(
        self,
        species: Species,
        alleles: Sequence[ResultWithSpecies],
        raw_string: Union[str, None] = None,
    ):
        name = "/".join(_short_name(a) for a in alleles)
        ResultWithMultipleAlleles.__init__(
            self, species=species, name=name, alleles=alleles, raw_string=raw_string
        )

    def to_string(self, include_species=True, use_old_species_prefix=False):
        parts = [
            a.to_string(include_species=False, use_old_species_prefix=use_old_species_prefix)
            for a in self.alleles
        ]
        joined = "/".join(parts)
        if include_species:
            species_str = self.species.to_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix,
            )
            return f"{species_str}-{joined}"
        return joined

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )

    def to_record(self):
        d = self.species.to_record()
        d["ambiguous_alleles"] = self.to_string()
        return d

    @property
    def mhc_class(self):
        # Share a single mhc_class across members when they agree (e.g.
        # all class I); otherwise None.
        classes = {getattr(a, "mhc_class", None) for a in self.alleles}
        classes.discard(None)
        if len(classes) == 1:
            return next(iter(classes))
        return None

    @property
    def has_mhc_class(self):
        return self.mhc_class is not None


def _short_name(allele):
    if hasattr(allele, "compact_string"):
        return allele.compact_string(include_species=False)
    return getattr(allele, "name", str(allele))
