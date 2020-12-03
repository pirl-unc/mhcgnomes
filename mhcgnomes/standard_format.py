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

import re
from typing import Union

from .species import Species
from .gene import Gene
from .allele import Allele

_standard_allele_regex_str = (
    "([a-zA-Z]+-)?"             # optional species
    "([a-zA-Z]+\d?|\d{1,2})\*"  # gene, either e.g. "A1" or "88"
    "(\d{2,3})"     # mandatory first digit field with between 2 and 3 digits
    "(:\d{2,3})?"   # optional second allele field with up to 3 digits
    "(:\d\d)?"      # optional third allele field
    "(:\d\d)?"      # optional fourth allele field
    "([a-zA-Z])?"       # optional annotation at the end of the allele
)
_standard_allele_regex = re.compile(_standard_allele_regex_str)


def parse_standard_allele_format(
        seq: str,
        raw_string: Union[str, None] = None,
        default_species: Union[str, Species, None] = None):
    """
    Parse alleles which are in a standard format, such as::

        Species-Gene*001:01:01:01

    Between one and four allele fields are allowed and the number of digits
    must be 2 or 3 in the first two fields and exactly two in the last two
    fields. A single character annotation is allowed at the end.

    Parameters
    ----------
    seq : str
        Sequence to parse

    raw_string : str
        Raw string the sequence was derived from

    default_species : str, Species, or None
        If no species is provided in the sequence, should one be assumed?

    Returns
    -------
    Allele or None
    """
    match = _standard_allele_regex.fullmatch(seq)

    if not match:
        return None

    groups = match.groups()

    if len(groups) < 3:
        return None

    species_prefix, gene_name = groups[:2]

    if gene_name is None:
        return None

    if species_prefix is None:
        species = Species.get(default_species)
    elif len(species_prefix) >= 2 and species_prefix[-1] == "-":
        species = Species.get(species_prefix[:-1])
    else:
        return None

    if species is None:
        return None

    gene = Gene.get(species, gene_name)

    if gene is None:
        return None

    allele_fields = []
    for i, raw_allele_field in enumerate(groups[2:-1]):
        if raw_allele_field is None:
            break
        elif i == 0:
            allele_fields.append(raw_allele_field)
        else:
            # skip the initial ':' in all fields after first
            allele_fields.append(raw_allele_field[1:])

    if len(allele_fields) == 0:
        return None

    annotation = groups[-1]

    if annotation:
        annotations = [annotation.upper()]
    else:
        annotations = []

    if raw_string is None:
        raw_string = seq

    return Allele.get_with_gene(
        gene,
        allele_fields,
        annotations=annotations,
        raw_string=raw_string)