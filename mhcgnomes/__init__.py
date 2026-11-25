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

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from .version import __version__

if TYPE_CHECKING:
    from .accessioned_allele import AccessionedAllele
    from .allele import Allele
    from .allele_without_gene import AlleleWithoutGene
    from .ambiguous_alleles import AmbiguousAlleles
    from .class2_locus import Class2Locus
    from .dataframe import dataframe_from_parsed_objects, dataframe_from_string_list
    from .errors import ParseError
    from .function_api import cached_parser, infer_mhc_class, parse, parse_gene_class
    from .gene import Gene
    from .gene_class_info import GeneClassInfo
    from .haplotype import Haplotype
    from .mhc_class import MhcClass
    from .mutation import Mutation
    from .normalizing_dictionary import NormalizingDictionary
    from .normalizing_set import NormalizingSet
    from .pair import Pair
    from .parse_outcome import parse_outcome_to_row
    from .parser import Parser
    from .registry_identity import (
        RegistryIdentity,
        get_registry_identities,
        get_registry_identity,
        registry_identities,
    )
    from .serotype import Serotype
    from .species import Species
    from .supertype import Supertype


LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "AccessionedAllele": (".accessioned_allele", "AccessionedAllele"),
    "Allele": (".allele", "Allele"),
    "AlleleWithoutGene": (".allele_without_gene", "AlleleWithoutGene"),
    "AmbiguousAlleles": (".ambiguous_alleles", "AmbiguousAlleles"),
    "Class2Locus": (".class2_locus", "Class2Locus"),
    "Gene": (".gene", "Gene"),
    "GeneClassInfo": (".gene_class_info", "GeneClassInfo"),
    "Haplotype": (".haplotype", "Haplotype"),
    "MhcClass": (".mhc_class", "MhcClass"),
    "Mutation": (".mutation", "Mutation"),
    "NormalizingDictionary": (".normalizing_dictionary", "NormalizingDictionary"),
    "NormalizingSet": (".normalizing_set", "NormalizingSet"),
    "Pair": (".pair", "Pair"),
    "ParseError": (".errors", "ParseError"),
    "Parser": (".parser", "Parser"),
    "RegistryIdentity": (".registry_identity", "RegistryIdentity"),
    "Serotype": (".serotype", "Serotype"),
    "Species": (".species", "Species"),
    "Supertype": (".supertype", "Supertype"),
    "cached_parser": (".function_api", "cached_parser"),
    "dataframe_from_parsed_objects": (".dataframe", "dataframe_from_parsed_objects"),
    "dataframe_from_string_list": (".dataframe", "dataframe_from_string_list"),
    "get_registry_identities": (".registry_identity", "get_registry_identities"),
    "get_registry_identity": (".registry_identity", "get_registry_identity"),
    "infer_mhc_class": (".function_api", "infer_mhc_class"),
    "parse": (".function_api", "parse"),
    "parse_gene_class": (".function_api", "parse_gene_class"),
    "parse_outcome_to_row": (".parse_outcome", "parse_outcome_to_row"),
    "registry_identities": (".registry_identity", "registry_identities"),
}

LAZY_SUBMODULES: frozenset[str] = frozenset(
    {
        "accessioned_allele",
        "allele",
        "allele_annotations",
        "allele_without_gene",
        "ambiguous_alleles",
        "class2_locus",
        "cli",
        "cli_help",
        "common",
        "data",
        "dataframe",
        "errors",
        "external_data",
        "function_api",
        "gene",
        "gene_class_info",
        "haplotype",
        "input_validation",
        "mhc_class",
        "mhc_class_helpers",
        "mutation",
        "non_mhc_genes",
        "normalizing_dictionary",
        "normalizing_set",
        "pair",
        "parse_outcome",
        "parser",
        "parsing_helpers",
        "prefix_display_policy",
        "registry_identity",
        "result",
        "result_sorting",
        "result_with_gene",
        "result_with_mhc_class",
        "result_with_multiple_alleles",
        "result_with_species",
        "serotype",
        "serotype_hierarchy",
        "species",
        "standard_format",
        "supertype",
        "token",
        "token_canonical_sequences",
        "token_substitution",
        "tokenize",
        "validate_external_names",
        "version",
    }
)

__all__ = [
    "AccessionedAllele",
    "Allele",
    "AlleleWithoutGene",
    "AmbiguousAlleles",
    "Class2Locus",
    "Gene",
    "GeneClassInfo",
    "Haplotype",
    "MhcClass",
    "Mutation",
    "NormalizingDictionary",
    "NormalizingSet",
    "Pair",
    "ParseError",
    "Parser",
    "RegistryIdentity",
    "Serotype",
    "Species",
    "Supertype",
    "cached_parser",
    "dataframe_from_parsed_objects",
    "dataframe_from_string_list",
    "get_registry_identities",
    "get_registry_identity",
    "infer_mhc_class",
    "parse",
    "parse_gene_class",
    "parse_outcome_to_row",
    "registry_identities",
]


def __getattr__(name: str) -> Any:
    target = LAZY_EXPORTS.get(name)
    if target is not None:
        module_name, attr_name = target
        module = importlib.import_module(module_name, __name__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    if name in LAZY_SUBMODULES:
        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
