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


class Supertype(ResultWithMultipleAlleles):
    """
    Represents an HLA supertype (functional peptide-binding group).

    A Supertype represents a group of HLA alleles that share similar peptide
    binding properties based on their B and F pocket chemistry. Unlike serotypes
    (which are based on antibody recognition), supertypes are defined by
    functional similarity in the peptides they can bind.

    The nine major HLA class I supertypes (A01, A02, A03, A24, B07, B08, B27,
    B44, B58, B62) were defined by Sidney, Sette et al. based on analysis of
    peptide-binding pockets.

    Note that supertype membership may differ from serotype classification.
    For example, A*68:02 is serologically A68 but belongs to the A02 supertype
    because it binds similar peptides to A*02:01.

    Parameters
    ----------
    species : Species
        The species this supertype belongs to (typically HLA/human).
    name : str
        The supertype name (e.g., "A01", "A02", "B07").
    alleles : Sequence[Allele]
        The alleles that belong to this supertype.
    representative : Allele, optional
        The representative/prototypic allele for this supertype.
    raw_string : str, optional
        The original unparsed string.

    Attributes
    ----------
    species : Species
        The species this supertype belongs to.
    name : str
        The supertype name.
    alleles : Sequence[Allele]
        The alleles in this supertype.
    representative : Allele or None
        The representative allele for this supertype.

    Examples
    --------
    >>> from mhcgnomes import parse
    >>> st = parse("A2 supertype")
    >>> st.name
    'A02'
    >>> len(st.alleles) > 0
    True

    References
    ----------
    Sidney J, Peters B, Frahm N, Brander C, Sette A. "HLA class I supertypes:
    a revised and updated classification." BMC Immunol. 2008;9:1.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC2245908/
    """

    def __init__(
        self,
        species: Species,
        name: str,
        alleles: Sequence[Allele],
        representative: Union[Allele, None] = None,
        raw_string: Union[str, None] = None,
    ):
        ResultWithMultipleAlleles.__init__(
            self, species=species, name=name, alleles=alleles, raw_string=raw_string
        )
        self.representative = representative

    def to_string(self, include_species=True, use_old_species_prefix=False):
        if include_species:
            prefix = self.species.to_string(use_old_species_prefix=use_old_species_prefix)
            return f"{prefix} {self.name} supertype"
        else:
            return f"{self.name} supertype"

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        if include_species:
            prefix = self.species.to_string(use_old_species_prefix=use_old_species_prefix)
            return f"{prefix}-{self.name}"
        else:
            return self.name

    def to_record(self):
        d = self.species.to_record()
        d["supertype"] = self.name
        d["supertype_string"] = self.to_string()
        if self.representative:
            d["representative_allele"] = self.representative.to_string()
        return d
