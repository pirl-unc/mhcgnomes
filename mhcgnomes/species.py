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
from collections import OrderedDict, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Union

from .common import cache
from .data import allele_aliases as raw_allele_aliases_dict
from .data import gene_aliases as raw_gene_aliases_dict
from .data import haplotypes as raw_haplotypes_dict
from .data import heterodimers as raw_heterodimers_dict
from .data import known_alleles as raw_known_alleles_dict
from .data import serotypes as raw_serotypes_dict
from .data import species as raw_species_dict
from .data import supertypes as raw_supertypes_dict
from .mhc_class_helpers import class1_restrictions, class2_restrictions
from .normalizing_dictionary import NormalizingDictionary
from .normalizing_set import NormalizingSet
from .result import Result


class FrozenList(list):
    def _immutable(self, *args, **kwargs):
        raise TypeError("FrozenList is immutable")

    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    __setitem__ = _immutable

    def copy(self):
        return list(self)


class FrozenSet(set):
    def _immutable(self, *args, **kwargs):
        raise TypeError("FrozenSet is immutable")

    add = _immutable
    clear = _immutable
    difference_update = _immutable
    discard = _immutable
    intersection_update = _immutable
    pop = _immutable
    remove = _immutable
    symmetric_difference_update = _immutable
    update = _immutable
    __ior__ = _immutable
    __iand__ = _immutable
    __isub__ = _immutable
    __ixor__ = _immutable

    def copy(self):
        return set(self)

    def __repr__(self):
        return repr(set(self))

    def __str__(self):
        return str(set(self))


def _ensure_normalizing_set(values):
    if values is None:
        return NormalizingSet()
    if isinstance(values, NormalizingSet):
        return values.copy()
    return NormalizingSet(*values)


def _ensure_normalizing_dictionary(values, default_value_fn=None):
    if values is None:
        return NormalizingDictionary(default_value_fn=default_value_fn)
    if isinstance(values, NormalizingDictionary):
        result = values.copy()
        if default_value_fn is not None and result.default_value_fn is None:
            result.default_value_fn = default_value_fn
        return result
    return NormalizingDictionary.from_dict(values, default_value_fn=default_value_fn)


def _freeze_nested_value(value):
    if isinstance(value, NormalizingDictionary):
        frozen_dict = value.copy()
        for key, subvalue in list(frozen_dict.items()):
            frozen_dict[key] = _freeze_nested_value(subvalue)
        return frozen_dict.freeze()
    if isinstance(value, NormalizingSet):
        return value.copy().freeze()
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze_nested_value(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return FrozenList(_freeze_nested_value(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return FrozenSet(_freeze_nested_value(v) for v in value)
    return value


@dataclass(eq=False, repr=False, frozen=True, init=False)
class Species(Result):
    """
    Representation of a parsed species prefix such as "HLA", "ELA"
    """

    name: str = ""
    common_name: str = ""
    mhc_prefix: str = ""
    gene_names: Any = None
    gene_name_to_mhc_class: Any = None
    class2_loci: Any = None
    class2_locus_to_gene_names: Any = None
    class2_gene_name_to_chain_type: Any = None
    gene_aliases: Any = None
    reverse_gene_aliases: Any = None
    allele_aliases: Any = None
    known_alleles: Any = None
    haplotypes: Any = None
    serotypes: Any = None
    heterodimers: Any = None
    supertypes: Any = None
    parent_species: Union["Species", None] = None
    old_mhc_prefix: str = ""
    other_mhc_prefixes: Any = None
    other_common_names: Any = None

    def __init__(
        self,
        name: str,
        common_name: str,
        mhc_prefix: str,
        gene_names: Iterable[str],
        gene_name_to_mhc_class: Mapping[str, str],
        class2_loci: Iterable[str],
        class2_locus_to_gene_names: Mapping[str, Iterable[str]],
        class2_gene_name_to_chain_type: Mapping[str, str],
        gene_aliases: Mapping[str, str],
        allele_aliases: Mapping[str, str],
        known_alleles: Mapping[str, Iterable[str]],
        haplotypes: Mapping[str, Iterable[str]],
        serotypes: Mapping[str, Iterable[str]],
        heterodimers: Mapping[str, Mapping[str, str]],
        supertypes: Mapping[str, Mapping[str, Any]],
        parent_species: Union["Species", None] = None,
        old_mhc_prefix: Union[str, None] = None,
        other_mhc_prefixes: Iterable[str] = [],
        other_common_names: Iterable[str] = [],
        raw_string: Union[str, None] = None,
    ):
        Result.__init__(self, raw_string=raw_string)

        gene_names = _ensure_normalizing_set(gene_names)
        gene_name_to_mhc_class = _ensure_normalizing_dictionary(gene_name_to_mhc_class)
        class2_loci = _ensure_normalizing_set(class2_loci)
        class2_locus_to_gene_names = _ensure_normalizing_dictionary(
            class2_locus_to_gene_names, default_value_fn=set
        )
        class2_gene_name_to_chain_type = _ensure_normalizing_dictionary(
            class2_gene_name_to_chain_type
        )
        gene_aliases = _ensure_normalizing_dictionary(gene_aliases)
        allele_aliases = _ensure_normalizing_dictionary(allele_aliases)
        known_alleles = _ensure_normalizing_dictionary(
            known_alleles, default_value_fn=NormalizingSet
        )
        known_alleles = known_alleles.map_values(_ensure_normalizing_set)
        haplotypes = _ensure_normalizing_dictionary(haplotypes)
        serotypes = _ensure_normalizing_dictionary(serotypes)
        heterodimers = _ensure_normalizing_dictionary(heterodimers)
        supertypes = _ensure_normalizing_dictionary(supertypes)

        self._set_field(self, "name", name)
        self._set_field(self, "common_name", common_name)
        self._set_field(self, "other_common_names", FrozenList(other_common_names))
        self._set_field(self, "mhc_prefix", mhc_prefix)
        self._set_field(self, "other_mhc_prefixes", FrozenSet(other_mhc_prefixes))
        if old_mhc_prefix:
            normalized_old_mhc_prefix = old_mhc_prefix
        else:
            normalized_old_mhc_prefix = mhc_prefix
        self._set_field(self, "old_mhc_prefix", normalized_old_mhc_prefix)

        self._set_field(self, "gene_names", _freeze_nested_value(gene_names))
        self._set_field(
            self, "gene_name_to_mhc_class", _freeze_nested_value(gene_name_to_mhc_class)
        )
        self._set_field(self, "class2_loci", _freeze_nested_value(class2_loci))
        self._set_field(
            self,
            "class2_locus_to_gene_names",
            _freeze_nested_value(class2_locus_to_gene_names),
        )
        self._set_field(
            self,
            "class2_gene_name_to_chain_type",
            _freeze_nested_value(class2_gene_name_to_chain_type),
        )
        self._set_field(self, "gene_aliases", _freeze_nested_value(gene_aliases))
        # create a reverse lookup from proper names to their list of aliases
        reverse_gene_aliases = self._create_reverse_gene_aliases(self.gene_names, self.gene_aliases)
        self._set_field(self, "reverse_gene_aliases", _freeze_nested_value(reverse_gene_aliases))

        self._set_field(self, "allele_aliases", _freeze_nested_value(allele_aliases))
        self._set_field(self, "known_alleles", _freeze_nested_value(known_alleles))
        self._set_field(self, "haplotypes", _freeze_nested_value(haplotypes))
        self._set_field(self, "serotypes", _freeze_nested_value(serotypes))
        self._set_field(self, "heterodimers", _freeze_nested_value(heterodimers))
        self._set_field(self, "supertypes", _freeze_nested_value(supertypes))
        self._set_field(self, "parent_species", parent_species)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if type(other) is not Species:
            return False
        return self.name == other.name

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    @classmethod
    def _create_reverse_gene_aliases(cls, gene_names, gene_aliases):
        """
        Creates dictionary mapping canonical gene name to its set of aliases.
        """
        d = defaultdict(NormalizingSet)

        for k, v in gene_aliases.items():
            d[v].add(k)
        for v in gene_names:
            d[v].add(v)
        return d

    @classmethod
    def str_field_names(cls):
        return ("name", "mhc_prefix")

    @classmethod
    def tuple_field_names(cls):
        return ("name", "mhc_prefix")

    @classmethod
    def eq_field_names(cls):
        return ("name",)

    @classmethod
    def from_dict(cls, d):
        if "name" in d:
            species_name = d["name"]
            return species_name_to_species_object.get(species_name)
        return None

    @property
    def species_name(self):
        return self.name

    @property
    def canonical_mhc_prefix(self):
        return self.mhc_prefix

    @property
    def parent(self):
        return self.parent_species

    # TODO: If taxonomy-aware operations keep expanding, promote these lineage
    # helpers into a fuller Taxon API instead of growing Species ad hoc.
    def is_parent_of(self, other):
        other = Species.get(other)
        return other is not None and other.parent_species == self

    def is_child_of(self, other):
        other = Species.get(other)
        return other is not None and self.parent_species == other

    def is_ancestor_of(self, other):
        other = Species.get(other)
        if other is None:
            return False
        current = other.parent_species
        while current is not None:
            if current == self:
                return True
            current = current.parent_species
        return False

    def is_descendant_of(self, other):
        other = Species.get(other)
        if other is None:
            return False
        current = self.parent_species
        while current is not None:
            if current == other:
                return True
            current = current.parent_species
        return False

    @property
    def historic_mhc_prefix(self):
        """
        Return older species name which is now used to group multiple
        related species (e.g. "DLA" for "Calu").
        """
        return self.old_mhc_prefix

    @property
    def historic_alias(self):
        return self.historic_mhc_prefix

    @property
    def gene_names_and_aliases(self):
        name_set = set(self.gene_aliases.keys()).union(self.gene_names)
        return sorted(name_set)

    @property
    def num_genes(self):
        return len(self.gene_names)

    @property
    def scientific_species_name(self):
        return self.name

    @property
    def latin_name(self):
        return self.name

    @property
    def species_prefix(self):
        return self.canonical_mhc_prefix

    @property
    def prefix(self):
        return self.species_prefix

    def to_string(self, include_species=True, use_old_species_prefix=False):
        if not include_species:
            return ""
        elif use_old_species_prefix:
            return self.historic_alias
        else:
            return self.prefix

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )

    @classmethod
    @cache
    def get_multiple(cls, species_name):
        """
        Cached wrapper around find_matching_species which tries to
        identify one or more species from any of its scientific name,
        common names, MHC prefixes.
        """
        return tuple(find_matching_species_objects(species_name))

    @classmethod
    @cache
    def get(cls, species_name):
        """
        Look up a species by any identifier (latin name, prefix, common name).
        Returns None if no match or if the alias is ambiguous (maps to
        multiple species). Use get_multiple() to retrieve all candidates
        for an ambiguous alias.
        """
        if type(species_name) is Species:
            return species_name
        elif species_name is None or type(species_name) is not str:
            return None

        species_objects = cls.get_multiple(species_name)

        # Try underscore-to-space normalization if no results
        # (common in bioinformatics: "Canis_lupus" for "Canis lupus")
        if len(species_objects) == 0 and "_" in species_name:
            species_objects = cls.get_multiple(species_name.replace("_", " "))

        if len(species_objects) == 0:
            return None
        if len(species_objects) == 1:
            return species_objects[0]
        # Multiple species match — try to find an unambiguous winner:
        # 1. Exact latin name match
        for sp in species_objects:
            if sp.name == species_name:
                return sp
        # 2. Exact primary prefix match (only one species should own a prefix)
        prefix_matches = [
            sp
            for sp in species_objects
            if sp.prefix.lower().strip() == species_name.lower().strip()
        ]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        # 3. For auto-generated long prefixes (e.g., CanisLupus), prefer
        # the species that isn't a subspecies (no parent with same identifier)
        non_child = [sp for sp in species_objects if sp.parent_species is None]
        if len(non_child) == 1:
            return non_child[0]
        # Ambiguous alias: return None instead of picking a heuristic winner
        return None

    @classmethod
    @cache
    def get_by_latin_name(cls, latin_name):
        """
        Look up a species by its scientific (latin) name.
        This is the canonical identity lookup and is never ambiguous.
        """
        return latin_name_to_species_object.get(latin_name)

    def to_record(self):
        return OrderedDict(
            [
                ("species_prefix", self.prefix),
                ("species_name", self.name),
                ("species_latin_name", self.latin_name),
            ]
        )

    @property
    def common_species_name(self):
        """
        Returns common species name associated with MHC species
        prefix.
        """
        return self.common_name

    @property
    def all_mhc_prefixes(self):
        """
        Returns all MHC prefixes used for this species
        """
        prefixes = set(self.other_mhc_prefixes)
        if self.old_mhc_prefix and self.old_mhc_prefix != self.prefix:
            prefixes.add(self.old_mhc_prefix)
        return [self.prefix, *sorted(prefixes)]

    @property
    def all_common_names(self):
        """
        Returns all common names used for this species
        """
        return [self.common_name, *self.other_common_names]

    @property
    def all_identifiers(self):
        """
        Return all names and prefixes associated with this Species.

        Returns list of str
        """
        return [self.name, *self.all_mhc_prefixes, *self.all_common_names]

    def find_matching_gene_name(self, gene_name):
        """
        Use known aliases and normalized capitalization to infer
        the canonical gene name corresponding to the input.

        Returns str or None
        """
        if type(gene_name) in (int, float):
            gene_name = str(gene_name)
        if gene_name in self.gene_names:
            return self.gene_names.get_original(gene_name)
        elif gene_name in self.gene_aliases:
            alt_gene_name = self.gene_aliases[gene_name]
            if alt_gene_name in self.gene_names:
                # make sure the new gene name is a gene name
                # and not a locus
                # e.g. H2-IA -> H2-A is a mapping of loci
                return alt_gene_name
        # Strip ZFIN-style "mhc1"/"mhc2" prefix from gene tokens
        # (e.g. "mhc1uba" → "UBA", "mhc2daa" → "DAA"). This is a
        # convention used in zebrafish and potentially other fish species.
        lower = gene_name.lower()
        for prefix in ("mhc1", "mhc2"):
            if lower.startswith(prefix) and len(gene_name) > len(prefix):
                stripped = gene_name[len(prefix) :]
                if stripped in self.gene_names:
                    return self.gene_names.get_original(stripped)
        return None

    def find_matching_class2_locus_name(self, locus_name):
        """
        Use known aliases and normalized capitalization to infer
        the canonical gene name corresponding to the input.

        Returns str or None
        """
        if type(locus_name) in (int, float):
            locus_name = str(locus_name)
        if locus_name in self.class2_loci:
            return self.class2_loci.get_original(locus_name)
        elif locus_name in self.gene_aliases:
            alt_locus_name = self.gene_aliases[locus_name]
            if alt_locus_name in self.class2_loci:
                # make sure the new locus name is an actual locus
                # and not a gene
                # e.g.
                # H2-IA -> H2-A is a mapping of loci
                # but
                # H2-IAb -> H2-Ab is a mppaing of genes
                return alt_locus_name
        return None

    def normalize_gene_name_if_exists(self, gene_name):
        normalized_name = self.find_matching_gene_name(gene_name)

        if normalized_name:
            return normalized_name
        else:
            return gene_name

    def get_mhc_class_of_gene(self, gene_name):
        """
        Parameters
        ----------
        gene_name : str

        Returns either one of:
            {"I", "Ia", "Ib", "Ic", "Id", "II", IIa", "IIb", "other"}
        or None if gene can't be found
        """
        gene_name = self.normalize_gene_name_if_exists(gene_name)
        return self.gene_name_to_mhc_class.get(gene_name)

    def get_known_allele(self, gene_name, allele_name):
        gene_name_candidates = {gene_name}

        if gene_name is not None:
            gene_aliases = self.reverse_gene_aliases.get(gene_name, [])
            gene_name_candidates.update(gene_aliases)

        for gene_name in gene_name_candidates:
            known_alleles_for_gene_name = self.known_alleles.get(gene_name)
            if known_alleles_for_gene_name and allele_name in known_alleles_for_gene_name:
                known_allele_name = known_alleles_for_gene_name.get_original(allele_name)
                return (gene_name, known_allele_name)

        # if allele isn't in known_alleles but it's an alias for an allele which
        # is, then also return it
        for gene_name in gene_name_candidates:
            if gene_name:
                key = f"{gene_name}*{allele_name}"
            else:
                key = allele_name
            if key in self.allele_aliases:
                new_name = self.allele_aliases[key]
                for gene_name2 in gene_name_candidates:
                    if new_name in self.known_alleles.get(gene_name2, []):
                        known_allele_name = self.allele_aliases.original_key(key)
                        return (gene_name, known_allele_name)
        return None

    @cache
    def get_allele_alias(self, gene_name: str, allele_name: str):
        """
        Returns None if no alias found, otherwise pair of
        (gene name, allele name)
        """
        gene_name_candidates = {gene_name}

        if gene_name is not None:
            gene_aliases = self.reverse_gene_aliases.get(gene_name, [])
            gene_name_candidates.update(gene_aliases)

        # if allele isn't in known_alleles try looking at the keys of
        # allele_aliases
        for gene_name in gene_name_candidates:
            if gene_name:
                key = f"{gene_name}*{allele_name}"
            else:
                key = allele_name
            if key in self.allele_aliases:
                value = self.allele_aliases[key]
                if "*" in value:
                    parts = value.split("*")
                    if len(parts) != 2:
                        continue
                    return tuple(parts)
                else:
                    return (None, value)
        return None

    @classmethod
    def get_species_with_gene_name(self, gene_name):
        """
        Returns list of Species which have the given gene name
        """
        if gene_name in gene_name_to_species_objects:
            return list(gene_name_to_species_objects[gene_name])
        else:
            return []

    @property
    def is_mouse(self):
        return self.prefix in {"H-2", "H2"}

    @property
    def is_chicken(self):
        return self.prefix == "Gaga"

    @property
    def is_rat(self):
        return self.prefix in {"RT1", "Rano"}

    @property
    def is_human(self):
        return self.prefix == "HLA"

    @property
    def is_dog(self):
        return self.prefix in {"DLA", "Calu"}

    @property
    def is_cat(self):
        return self.prefix in {"FLA", "Feca"}

    @property
    def is_pig(self):
        return self.prefix in {"SLA", "Susc"}

    @property
    def is_cow(self):
        return self.prefix == "BoLA"

    @property
    def is_horse(self):
        return self.prefix in {"ELA", "Eqca"}


################################################################################
#
# Parse the species/gene ontology and create dictionaries mapping
# to Species objects
#
################################################################################


def guess_class2_chain_type(gene_name):
    # For now we're guessing based on the name, e.g.
    # DRB1 is a beta chain and DRA is an alpha chain
    trimmed_gene_name = gene_name
    if trimmed_gene_name.endswith("like"):
        trimmed_gene_name = trimmed_gene_name[:-4]
    while trimmed_gene_name and trimmed_gene_name[-1].isdigit():
        trimmed_gene_name = trimmed_gene_name[:-1]
    if not trimmed_gene_name:
        return "beta"
    last_letter = trimmed_gene_name[-1].upper()
    is_alpha = last_letter == "A"
    # assume that anything which can't be pinned down to be an alpha chain
    # is then a beta chain, since more of the variability/gene copying
    # seems to occur in beta chains
    return "alpha" if is_alpha else "beta"


def _make_long_prefix(latin_name):
    """
    Generate a long prefix from a latin binomial name by taking the first
    5 characters of each word, capitalized. E.g.:
        "Chrysemys picta" → "ChrysPicta"
        "Bubo bubo" → "BuboBubo"
        "Mus musculus" → "MusMuscu"

    Returns None for names that don't have at least two words (e.g. "Bos sp.").
    """
    parts = latin_name.split()
    if len(parts) < 2 or parts[1].endswith("."):
        return None
    genus = parts[0][:5]
    species = parts[1][:5]
    return genus.capitalize() + species.capitalize()


def _is_taxonomic_prefix(prefix, latin_name):
    """
    Taxonomic helper prefixes like "Galliformes" or "Crocodylia" should not
    become inherited old MHC prefixes for child species.
    """
    normalized_prefix = re.sub(r"[^A-Za-z0-9]+", "", prefix).lower()
    latin_parts = [part for part in latin_name.split() if part.lower() != "sp."]
    if not latin_parts:
        return False
    normalized_first = re.sub(r"[^A-Za-z0-9]+", "", latin_parts[0]).lower()
    normalized_concat = "".join(re.sub(r"[^A-Za-z0-9]+", "", part).lower() for part in latin_parts)
    return normalized_prefix in {normalized_first, normalized_concat}


@cache
def create_species_for_latin_name(latin_name):
    if latin_name not in raw_species_dict:
        raise ValueError(f"Species not found: '{latin_name}'")
    species_info = raw_species_dict[latin_name]
    parent_species_latin_name = species_info.get("parent")
    if parent_species_latin_name:
        parent_species = create_species_for_latin_name(parent_species_latin_name)
    else:
        parent_species = None

    prefix = species_info.get("prefix")
    if not prefix:
        raise ValueError(f"Missing 'prefix' for '{latin_name}' in species ontology")

    old_mhc_prefix = species_info.get("old prefix")
    if not old_mhc_prefix and parent_species:
        parent_prefix = parent_species.prefix
        if not _is_taxonomic_prefix(parent_prefix, parent_species.name):
            old_mhc_prefix = parent_prefix

    other_mhc_prefixes = species_info.get("other prefixes")
    if type(other_mhc_prefixes) is str:
        other_mhc_prefixes = [other_mhc_prefixes]
    elif other_mhc_prefixes is None:
        other_mhc_prefixes = []

    # Auto-generate parseable aliases from the latin name:
    # 1. A 5+5 long prefix (e.g. "ChrysPicta") for collision-free short form
    # 2. The full concatenated latin name (e.g. "ChrysemysPicta") so that
    #    the untruncated form always works too
    long_prefix = _make_long_prefix(latin_name)
    parts = latin_name.split()
    full_concat = parts[0].capitalize() + parts[1].capitalize() if len(parts) >= 2 else None
    for alias in [long_prefix, full_concat]:
        if alias and alias not in other_mhc_prefixes:
            other_mhc_prefixes = [*list(other_mhc_prefixes), alias]

    common_name = species_info.get("name")
    if not common_name:
        raise ValueError(f"Missing 'name' for '{latin_name}' in species ontology")

    if type(common_name) is str:
        common_names = [common_name]
    else:
        common_names = common_name
    # make all common names lowercase
    common_names = [s.lower() for s in common_names]
    shortest_common_name = min(common_names, key=len)

    if parent_species is None:
        gene_names = NormalizingSet()
        gene_name_to_mhc_class = NormalizingDictionary()
        class2_loci = NormalizingSet()
        class2_locus_to_gene_names = NormalizingDictionary(default_value_fn=set)
        class2_gene_name_to_chain_type = NormalizingDictionary()
    else:
        gene_names = parent_species.gene_names.copy()
        gene_name_to_mhc_class = parent_species.gene_name_to_mhc_class.copy()
        class2_loci = parent_species.class2_loci.copy()
        class2_locus_to_gene_names = parent_species.class2_locus_to_gene_names.map_values(set)
        class2_gene_name_to_chain_type = parent_species.class2_gene_name_to_chain_type.copy()

    for mhc_class, mhc_class_members in species_info.get("genes", {}).items():
        if mhc_class_members is None:
            raise ValueError(
                f"Unexpected None in gene ontology for class '{mhc_class}' of '{latin_name}'"
            )
        if mhc_class in class1_restrictions.union({"other"}):
            if type(mhc_class_members) is not list:
                raise ValueError(
                    f"Malformed gene ontology for '{latin_name}' MHC class '{mhc_class}'"
                )
            for gene_name in mhc_class_members:
                gene_names.add(str(gene_name))
                gene_name_to_mhc_class[gene_name] = mhc_class
        elif mhc_class in class2_restrictions:
            if type(mhc_class_members) is not dict:
                raise ValueError(
                    f"Malformed gene ontology for '{latin_name}' MHC class '{mhc_class}'"
                )
            for locus, locus_gene_names in mhc_class_members.items():
                class2_loci.add(locus)
                for gene_name in locus_gene_names:
                    gene_name = str(gene_name)
                    gene_names.add(gene_name)
                    gene_name_to_mhc_class[gene_name] = mhc_class
                    class2_locus_to_gene_names[locus].add(gene_name)
                    # TODO:
                    #  make alpha vs. beta chain genes explicit in
                    #  the YAML file ontology
                    chain_type = guess_class2_chain_type(gene_name)
                    class2_gene_name_to_chain_type[gene_name] = chain_type

    # Side tables inherit by lineage, but parent prefixes/common names must not
    # become implicit aliases for child species.
    ancestor_latin_names = []
    current_parent = parent_species
    while current_parent is not None:
        ancestor_latin_names.append(current_parent.name)
        current_parent = current_parent.parent_species

    all_identifiers = list(reversed(ancestor_latin_names))
    all_identifiers.append(latin_name)
    all_identifiers.append(prefix)
    if old_mhc_prefix and old_mhc_prefix != prefix:
        all_identifiers.append(old_mhc_prefix)
    all_identifiers.extend(other_mhc_prefixes)
    all_identifiers.extend(common_names)

    # Don't rely on other YAML files to use any particular prefix or
    # species identifier, just try them all
    # One reason for this is that canonical species prefixes might change
    # over time and don't want one update to break code mysteriously
    # elsewhere. Another reason is that a few species share the same
    # prefix ('Bubu' belongs to both an owl species and water buffalo).
    gene_aliases = combine_species_aliases(raw_gene_aliases_dict, all_identifiers)
    allele_aliases = combine_species_aliases(raw_allele_aliases_dict, all_identifiers)
    haplotypes = combine_species_aliases(raw_haplotypes_dict, all_identifiers)
    serotypes = combine_species_aliases(raw_serotypes_dict, all_identifiers)
    heterodimers = combine_species_aliases(raw_heterodimers_dict, all_identifiers)
    supertypes = combine_species_aliases(raw_supertypes_dict, all_identifiers)
    known_alleles = combine_species_aliases(
        raw_known_alleles_dict, all_identifiers, value_class=NormalizingSet
    )

    return Species(
        name=latin_name,
        common_name=shortest_common_name,
        mhc_prefix=prefix,
        old_mhc_prefix=old_mhc_prefix,
        gene_names=gene_names,
        gene_name_to_mhc_class=gene_name_to_mhc_class,
        class2_loci=class2_loci,
        class2_locus_to_gene_names=class2_locus_to_gene_names,
        class2_gene_name_to_chain_type=class2_gene_name_to_chain_type,
        gene_aliases=gene_aliases,
        allele_aliases=allele_aliases,
        known_alleles=known_alleles,
        haplotypes=haplotypes,
        serotypes=serotypes,
        heterodimers=heterodimers,
        supertypes=supertypes,
        parent_species=parent_species,
        other_mhc_prefixes=other_mhc_prefixes,
        other_common_names=[name for name in common_names if name != shortest_common_name],
        raw_string=latin_name,
    )


def combine_species_aliases(
    species_dict, species_names, dictionary_class=NormalizingDictionary, value_class=None
):
    if value_class:
        result = dictionary_class(default_value_fn=value_class)
    else:
        result = dictionary_class()
    for species_name in species_names:
        value_for_species = species_dict.get(species_name)
        if value_for_species:
            if type(value_for_species) not in (dict, NormalizingDictionary):
                raise TypeError(f"Expected sub-dictionaries but got {type(value_for_species)}")
            for key, value in value_for_species.items():
                old_value = None
                if key in result:
                    old_value = result[key]
                elif value_class is not None:
                    old_value = value_class()

                if old_value is not None:
                    t = type(old_value)
                    if t in {set, dict, NormalizingSet, NormalizingDictionary}:
                        combined = old_value.copy()
                        combined.update(value)
                        value = combined
                    elif t in {list, tuple}:
                        value = old_value + t(value)
                result[key] = value
    return result


def create_species_lookup_dictionaries():
    gene_name_to_species_objects = NormalizingDictionary(default_value_fn=set)
    # Canonical index: latin name → species (never ambiguous)
    latin_name_to_species = NormalizingDictionary()
    # Legacy index kept for compatibility
    species_name_to_species = NormalizingDictionary()

    # latin name, common names, or MHC prefixes all mapping to multiple
    # species objects
    alias_to_species_objects = NormalizingDictionary(default_value_fn=set)

    for latin_name in raw_species_dict:
        species = create_species_for_latin_name(latin_name)
        latin_name_to_species[latin_name] = species
        species_name_to_species[latin_name] = species
        for s in species.all_identifiers:
            alias_to_species_objects[s].add(species)
        for gene_name in species.gene_names_and_aliases:
            gene_name_to_species_objects[gene_name].add(species)
    return (
        latin_name_to_species,
        species_name_to_species,
        alias_to_species_objects,
        gene_name_to_species_objects,
    )


(
    latin_name_to_species_object,
    species_name_to_species_object,
    alias_to_species_objects,
    gene_name_to_species_objects,
) = create_species_lookup_dictionaries()


def find_matching_species_objects(name):
    """
    Returns list of Species
    """
    if type(name) is Species:
        return [name]
    if name is None:
        return []
    return list(alias_to_species_objects.get(name, []))


def create_species_sort_key(query_string):
    """
    If we get multiple Species matching a query then
    use this key function to sort possible matches
    and prefer ones that match the query best.
    """

    def sort_key(species):
        same_prefix = species.prefix == query_string
        similar_prefix = species.prefix.lower().strip() == query_string.lower().strip()
        num_genes = species.num_genes
        return (same_prefix, similar_prefix, num_genes)

    return sort_key


def infer_species_from_prefix(name, _allow_mhc_strip=True):
    """
    Trying to parse prefixes of alleles such as:
        HLA-A
    but also ones with dashes in the species prefix:
        H-2-K
    and also those lacking any dashes such as:
        H2K

     ...we also need to consider that alleles, haplotypes, etc may come
     immediately after the gene:
        H2Kk
        HLA-A0201

    Returns the Species and the original string that matched it or None.
    """
    # Try parsing a few different substrings to get the species,
    # and then use the species gene list to determine what the gene is in this string
    candidate_species_substrings = {name}

    if "-" in name or "." in name:
        # if name is "H-2-K" or "RT1.A" then try parsing "H", "H-2", "RT1" as
        # species prefixes. We treat both "-" and "." as valid separators.
        parts_split_by_separator = re.split(r"[-.]", name)
        candidate_species_substrings.add(parts_split_by_separator[0])
        if len(parts_split_by_separator) > 1:
            # Also try first two parts joined by hyphen (e.g., "H-2" from "H-2-K")
            candidate_species_substrings.add(
                parts_split_by_separator[0] + "-" + parts_split_by_separator[1]
            )

    for num_chars in [None, 4, 3, 2]:
        for candidate in candidate_species_substrings:
            if num_chars:
                original_prefix = candidate[:num_chars]
            else:
                original_prefix = candidate
            species_objects = find_matching_species_objects(original_prefix)
            if species_objects:
                if len(species_objects) == 1:
                    return species_objects[0], original_prefix
                # Multiple species match this prefix. Try disambiguation:
                # 1. If exactly one species owns this as its primary prefix,
                #    use it (covers parent/child cases like SLA, BoLA, RT1).
                prefix_owners = [
                    sp
                    for sp in species_objects
                    if sp.prefix.lower().strip() == original_prefix.lower().strip()
                ]
                if len(prefix_owners) == 1:
                    return prefix_owners[0], original_prefix
                # 2. Try gene-context disambiguation from the remaining string.
                remaining = name[len(original_prefix) :]
                remaining = remaining.lstrip("-. ")
                before_star = remaining.split("*")[0] if remaining else ""
                gene_candidates = [before_star] if before_star else []
                parts = re.split(r"[-.]", before_star)
                for i in range(len(parts) - 1, 0, -1):
                    gene_candidates.append("-".join(parts[:i]))
                for gene_token in gene_candidates:
                    compatible = [
                        sp
                        for sp in species_objects
                        if sp.find_matching_gene_name(gene_token) is not None
                    ]
                    if len(compatible) == 1:
                        return compatible[0], original_prefix
                # Could not disambiguate — skip this candidate length and
                # try shorter prefixes or other strategies.
                continue

    # Strip a leading "Mhc" prefix commonly seen in bird MHC literature
    # (e.g., "MhcTyal-DAB1*01:01" → "Tyal-DAB1*01:01"). Only attempted
    # once (_allow_mhc_strip flag prevents recursive stripping) and only
    # after normal prefix matching has failed, so a direct prefix match
    # is always preferred.
    if _allow_mhc_strip and len(name) > 3 and name[:3].lower() == "mhc":
        stripped = name[3:]
        result = infer_species_from_prefix(stripped, _allow_mhc_strip=False)
        if result is not None:
            species_object, inner_prefix = result
            # Return the full original prefix including "Mhc" so the caller
            # can correctly compute the remaining string.
            return species_object, name[: 3 + len(inner_prefix)]

    # if all else fails, look for a distinctive gene name which is unique
    # to one species
    if "*" in name:
        parts = name.split("*")
        prefix = parts[0]
        species_objects = Species.get_species_with_gene_name(prefix)
        if len(species_objects) == 1:
            species = species_objects[0]
            # returning an empty string as the second result since no
            # part of the original string actually matched a species name
            # or alias but we inferred it from a gene name
            return species, ""
    return None
