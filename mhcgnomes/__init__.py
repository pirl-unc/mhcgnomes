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

from .allele import Allele
from .class2_locus import Class2Locus
from .class2_pair import Class2Pair
from .dataframe import dataframe_from_string_list, dataframe_from_parsed_objects
from .errors import ParseError
from .function_api import normalized_string, compact_string, parse
from .gene import Gene
from .haplotype import Haplotype
from .mutation import Mutation
from .mhc_class import MhcClass
from .normalizing_dictionary import NormalizingDictionary
from .normalizing_set import NormalizingSet
from .parser import Parser
from .serotype import Serotype
from .species import Species
from .allele_without_gene import AlleleWithoutGene

__version__ = "1.0.0"

__all__ = [
    "Allele",
    "Class2Locus",
    "Class2Pair",
    "Gene",
    "Haplotype",
    "MhcClass",
    "Mutation",
    "NormalizingDictionary",
    "NormalizingSet",
    "Parser",
    "ParseError",
    "Serotype",
    "Species",

    "compact_string",
    "dataframe_from_parsed_objects",
    "dataframe_from_string_list",
    "normalized_string",
    "parse",
]
