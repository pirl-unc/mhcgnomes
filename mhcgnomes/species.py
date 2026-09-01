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

from .common import cache, normalize_string
from .data import allele_aliases as raw_allele_aliases_dict
from .data import evidenced_prefix_aliases as raw_evidenced_alias_dict
from .data import gene_aliases as raw_gene_aliases_dict
from .data import haplotypes as raw_haplotypes_dict
from .data import heterodimers as raw_heterodimers_dict
from .data import known_alleles as raw_known_alleles_dict
from .data import serotypes as raw_serotypes_dict
from .data import species as raw_species_dict
from .data import supertypes as raw_supertypes_dict
from .data import underrepresented_taxa_source_registry as raw_holdback_registry
from .mhc_class_helpers import class1_restrictions, class2_restrictions
from .normalizing_dictionary import NormalizingDictionary
from .normalizing_set import NormalizingSet
from .result import Result

_RAW_SPECIES_ORDER = {latin_name: i for i, latin_name in enumerate(raw_species_dict)}


def _blocked_registry_prefixes():
    """
    Prefixes the curation registry deliberately keeps out of runtime.

    `underrepresented_taxa_source_registry.yaml` is the holding area described
    in docs/curation.md: real source signal that is not stable enough to parse
    with. An entry marked `blocked` or `registry_only` stays out no matter how
    well attested the spelling is.
    """
    blocked = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, dict) and "scientific_name" in value:
                    if (
                        value.get("curation_status") == "blocked"
                        or value.get("ontology_status") == "registry_only"
                    ):
                        blocked.add(normalize_string(key))
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(raw_holdback_registry)
    return blocked


def _partition_evidenced_aliases():
    """
    Split the attested aliases into globally parseable and context-only.

    The rule is computed rather than curated, so it cannot go stale as species
    are added: an alias claimed by exactly one species, and not already the
    prefix or alias of some other entry, becomes a global alias. Anything
    claimed by two or more -- or already owned elsewhere in species.yaml --
    becomes context-only, so `species=` recovers the published record while a
    bare prefix cannot silently pick a side. See issue #136.
    """
    withheld = _blocked_registry_prefixes()

    claimants = defaultdict(set)
    for latin_name, entries in raw_evidenced_alias_dict.items():
        for entry in entries or []:
            alias = normalize_string(entry["alias"])
            if alias not in withheld:
                claimants[alias].add(latin_name)

    already_claimed = set()
    for record in raw_species_dict.values():
        already_claimed.add(normalize_string(record.get("prefix", "")))
        for alias in record.get("other prefixes") or []:
            already_claimed.add(normalize_string(alias))

    global_aliases = defaultdict(list)
    context_only = defaultdict(list)
    for latin_name, entries in raw_evidenced_alias_dict.items():
        for entry in entries or []:
            alias = entry["alias"]
            key = normalize_string(alias)
            if len(alias) < 3:
                # A one- or two-character alias cannot safely be a species
                # prefix: "B" is real chicken nomenclature (B-F, B-L) but as a
                # bare prefix it shadows the mouse haplotype b, and b/d stops
                # parsing. Same reason the single-letter HLA fragments stay out
                # of unprefixed resolution (#113).
                continue
            if key in withheld:
                # underrepresented_taxa_source_registry.yaml is the holding area
                # for prefixes deliberately kept out of runtime. An attested
                # source spelling does not override that decision -- Otel, Phco
                # and Phtr are blocked there and tests assert they do not parse.
                continue
            contested = len(claimants[key]) > 1 or key in already_claimed
            (context_only if contested else global_aliases)[latin_name].append(alias)
    return dict(global_aliases), dict(context_only)


EVIDENCED_GLOBAL_ALIASES, EVIDENCED_CONTEXT_ONLY_ALIASES = _partition_evidenced_aliases()


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
    gene_name_to_properties: Any = None
    gene_family_name_to_gene_names: Any = None
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
    context_only_mhc_prefixes: Any = None
    other_common_names: Any = None
    prefix_provenance: Union[str, None] = None

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
        context_only_mhc_prefixes: Iterable[str] = [],
        other_common_names: Iterable[str] = [],
        prefix_provenance: Union[str, None] = None,
        raw_string: Union[str, None] = None,
        gene_name_to_properties: Union[Mapping[str, Mapping[str, Any]], None] = None,
        gene_family_name_to_gene_names: Union[Mapping[str, Iterable[str]], None] = None,
    ):
        Result.__init__(self, raw_string=raw_string)

        gene_names = _ensure_normalizing_set(gene_names)
        gene_name_to_mhc_class = _ensure_normalizing_dictionary(gene_name_to_mhc_class)
        gene_name_to_properties = _ensure_normalizing_dictionary(gene_name_to_properties)
        gene_family_name_to_gene_names = _ensure_normalizing_dictionary(
            gene_family_name_to_gene_names
        )
        gene_family_name_to_gene_names = gene_family_name_to_gene_names.map_values(
            _ensure_normalizing_set
        )
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
        self._set_field(
            self,
            "context_only_mhc_prefixes",
            FrozenSet(context_only_mhc_prefixes),
        )
        self._set_field(self, "prefix_provenance", prefix_provenance)
        if old_mhc_prefix:
            normalized_old_mhc_prefix = old_mhc_prefix
        else:
            normalized_old_mhc_prefix = mhc_prefix
        self._set_field(self, "old_mhc_prefix", normalized_old_mhc_prefix)

        self._set_field(self, "gene_names", _freeze_nested_value(gene_names))
        self._set_field(
            self, "gene_name_to_mhc_class", _freeze_nested_value(gene_name_to_mhc_class)
        )
        self._set_field(
            self,
            "gene_name_to_properties",
            _freeze_nested_value(gene_name_to_properties),
        )
        self._set_field(
            self,
            "gene_family_name_to_gene_names",
            _freeze_nested_value(gene_family_name_to_gene_names),
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

    def compatible_with(self, other):
        """
        Can these two species names describe the same sample?

        True when they are the same species, or when one is an ancestor of the
        other. Species legitimately differ in specificity: BoLA belongs to the
        genus-level "Bos sp.", so a BoLA-N*013:01 allele on a sample curated as
        Bos taurus is less specific, not contradictory.

            Bos taurus        vs Bos sp.               -> True  (ancestor)
            Coturnix japonica vs Galliformes sp.       -> True  (above genus)
            Homo sapiens      vs Primata sp.           -> True  (humans are primates)
            Homo sapiens      vs NHP                   -> False (a sibling group)
            Macaca mulatta    vs Macaca fascicularis   -> False (siblings)
            Carassius gibelio vs Homo sapiens          -> False

        Note that "shares a common ancestor" is NOT a usable test in its place:
        every species descends from "Gnathostomata sp.", so that predicate is
        true for any pair and fails open. Only a direct ancestor or descendant
        relation is meaningful, which is what this checks.

        Accepts a Species, a prefix, a common name or a latin name. Returns
        False if the other name does not resolve to a species at all.
        """
        other = Species.get(other)
        if other is None:
            return False
        return self == other or self.is_ancestor_of(other) or other.is_ancestor_of(self)

    @property
    def is_group(self):
        """
        Does this entry stand for a grouping rather than one species?

        True for every "<taxon> sp." node and for any entry declaring
        `group: true` -- currently NHP, IPD-MHC's non-human primate section,
        which is not a taxon and so cannot announce itself by name (#122).

        Exposed because the alternative is every consumer re-deriving it from
        `name.endswith(" sp.")`, which gets NHP wrong. See #135.
        """
        return _is_group_entry(self.name)

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
    def own_gene_names(self):
        """
        Genes declared by this species' own entry in the ontology, without the
        ones it inherits from an ancestor.

        A broad parent group makes every gene it defines visible to every
        species beneath it, so gene_names alone cannot tell you whether a
        species actually uses a name. Coturnix japonica inherits BLB1/BLB2
        from "Galliformes sp." and never declares them; Gallus gallus does.
        """
        return latin_name_to_own_gene_names.get(self.name, _EMPTY_GENE_NAMES)

    def declares_gene(self, gene_name):
        """
        Does this species' own ontology entry declare this gene, as opposed to
        inheriting it from an ancestor? Matching is normalized, the same way
        gene lookup is.
        """
        return gene_name in self.own_gene_names

    def declares_gene_with_same_case(self, gene_name):
        """
        Like declares_gene, but only when the declared spelling matches the
        query exactly. Gene lookup is case-normalizing, so "Ia1" (Paralichthys
        olivaceus) and "IA1" (Chrysolophus pictus) collide; the species that
        spells it the way the caller did is the better match.
        """
        return self.own_gene_names.get_original(gene_name) == gene_name

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
        normalized_query = species_name

        # Try underscore-to-space normalization if no results
        # (common in bioinformatics: "Canis_lupus" for "Canis lupus")
        if len(species_objects) == 0 and "_" in species_name:
            normalized_query = species_name.replace("_", " ")
            species_objects = cls.get_multiple(normalized_query)

        # Fall back from decorated scientific names to the longest valid
        # scientific-name prefix already present in the ontology.
        if len(species_objects) == 0:
            for candidate_name in _decorated_scientific_name_candidates(normalized_query):
                species_objects = cls.get_multiple(candidate_name)
                if len(species_objects) > 0:
                    break

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
        # Try replacing trailing "alpha"/"beta" with single-letter chain
        # suffix (e.g. "DOalpha" → "DOa", "Ebeta" → "Eb").
        for suffix, replacement in (("alpha", "a"), ("beta", "b")):
            if lower.endswith(suffix) and len(gene_name) > len(suffix):
                candidate = gene_name[: -len(suffix)] + replacement
                if candidate in self.gene_names:
                    return self.gene_names.get_original(candidate)
        return None

    def find_matching_gene_family_name(self, family_name):
        """Return the canonical name of an exact, ontology-backed gene family."""
        if type(family_name) in (int, float):
            family_name = str(family_name)
        if family_name in self.gene_family_name_to_gene_names:
            return self.gene_family_name_to_gene_names.original_key(family_name)
        return None

    def get_gene_family_members(self, family_name):
        """Return canonical member names for an ontology-backed gene family."""
        canonical_family_name = self.find_matching_gene_family_name(family_name)
        if canonical_family_name is None:
            return None
        return tuple(sorted(self.gene_family_name_to_gene_names[canonical_family_name]))

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

    def get_gene_properties(self, gene_name):
        """Return immutable ontology properties for a canonical gene."""
        gene_name = self.find_matching_gene_name(gene_name)
        if gene_name is None:
            return None
        return self.gene_name_to_properties.get(gene_name, MappingProxyType({}))

    def gene_has_no_alleles(self, gene_name):
        """
        Does this locus name alleles at all?

        A few loci are named by a nomenclature authority that deposits no
        sequence for them: IPD-IMGT/HLA 3.65.0 lists HLA-X, HLA-Z, HLA-DQB3,
        HLA-DPA3, MICC, MICD, MICE, PSMB8 and PSMB9 as genes and gives every
        one of them zero alleles. Building "HLA-Z*01:01" out of such a name is
        the pattern issue #108 ruled out -- a confidently structured answer for
        an input that justifies nothing -- so the entry carries
        `alleles: none` and `Allele.get_with_gene` refuses it.

        Absence from IPD-IMGT/HLA is *not* what this flag means: CD1a-e, MR1
        and BTN3A1 are absent from it too because it does not curate them, and
        they vary. The flag says the authority names the locus and publishes no
        alleles under it. See issue #113.
        """
        properties = self.get_gene_properties(gene_name)
        return properties is not None and properties.get("alleles") == "none"

    def gene_is_context_only(self, gene_name):
        """
        Does this gene name resolve only once the species is already known?

        The species-level analogue is `context only prefixes`, and the reason
        is the same: the string is real but too contested to hand out to a
        caller who has not said which species they mean. Every HLA class I gene
        fragment is a single letter, and bare "N", "R", "S", "U" and "Z" are
        mouse and rat haplotype shorthand long before they are human gene
        fragments. Marked genes stay out of `get_species_with_gene_name`, so
        they never win a species-less parse, while `HLA-N` and
        `parse("N", species="Homo sapiens")` resolve normally. See issue #113.
        """
        # get_gene_properties returns None for a name this species does not
        # carry, and both callers ask about arbitrary strings.
        properties = self.get_gene_properties(gene_name)
        return properties is not None and properties.get("context only") is True

    def get_pseudogene_status_of_gene(self, gene_name):
        """Return explicit pseudogene status, or ``None`` when it is not curated."""
        properties = self.get_gene_properties(gene_name)
        if properties is None:
            return None
        return properties.get("pseudogene")

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
    def get_species_with_gene_name(self, gene_name, include_context_only: bool = False):
        """
        Returns list of Species which have the given gene name.

        Both callers use this to guess a species from a bare gene name, so by
        default genes marked `context only` are left out: they are real names
        which are too contested to imply a species on their own. Pass
        `include_context_only=True` to ask the raw ontology question instead.
        """
        species_objects = list(gene_name_to_species_objects.get(gene_name, []))
        if include_context_only:
            return species_objects
        return [s for s in species_objects if not s.gene_is_context_only(gene_name)]

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


def _scientific_name_parts(latin_name):
    parts = latin_name.split()
    if len(parts) < 2:
        return []
    if parts[1].endswith("."):
        return []
    return parts


def _make_long_prefix(latin_name):
    """
    Generate a 4+4 novel prefix from a latin binomial name by taking the first
    4 characters of each word, capitalized. E.g.:
        "Oryzias latipes" → "OryzLati"
        "Struthio camelus" → "StruCame"
        "Bubo bubo" → "BuboBubo"

    Returns None for names that don't have at least two words (e.g. "Bos sp.").
    """
    parts = _scientific_name_parts(latin_name)
    if len(parts) < 2:
        return None
    genus = parts[0][:4]
    species = parts[1][:4]
    return genus.capitalize() + species.capitalize()


def _make_full_scientific_prefix(latin_name):
    """
    Generate a collision-resistant scientific-name alias from the canonical
    binomial portion of the modeled scientific name. Examples:
        "Oryzias latipes" -> "OryziasLatipes"
        "Canis lupus baileyi" -> "CanisLupus"
    """
    parts = _scientific_name_parts(latin_name)
    if len(parts) < 2:
        return None
    return "".join(part.capitalize() for part in parts[:2])


def _make_generated_alias_counts(generator):
    counts = defaultdict(int)
    for latin_name in raw_species_dict:
        alias = generator(latin_name)
        if alias:
            counts[alias] += 1
    return counts


def _long_prefix_if_claimable(latin_name):
    """
    The 4+4 form only where the entry is allowed to claim it. Trinomials are
    excluded, so a subspecies does not veto its parent binomial's shorthand by
    deriving the same string.
    """
    if len(_scientific_name_parts(latin_name)) != 2:
        return None
    return _make_long_prefix(latin_name)


_GENERATED_LONG_PREFIX_COUNTS = _make_generated_alias_counts(_long_prefix_if_claimable)


def _auto_generated_prefixes_for_latin_name(latin_name):
    """
    The concatenated scientific name comes first: it is the default, and the
    only form that never collides. The 4+4 truncation follows as a shorthand,
    and only where it is globally unique.

    The 5+5 form ("HomoSapie") was removed in 3.42.0. It was a leftover of the
    pre-v3.12 scheme that 4cd6045 replaced, its own docstring described it as
    kept for backward compatibility, docs/curation.md never listed it, and no
    name in the bundled corpora or in the sibling mhcseqs dataset used one.
    """
    results = []

    # The concatenated scientific name is the default generated alias: it is
    # the only form with no collisions anywhere in the ontology. Added only for
    # modeled binomials -- trinomial/subspecies entries mint no generated alias
    # and are reached by their curated prefix or latin name.
    scientific_parts = _scientific_name_parts(latin_name)
    full_prefix = _make_full_scientific_prefix(latin_name)
    if full_prefix and len(scientific_parts) == 2:
        results.append(full_prefix)

    # The 4+4 truncation is kept because it is the curated prefix of 466
    # entries, but only where it is globally unique. It is a shorthand, not the
    # default: 4+4 collides (ChryPict is derivable from both a painted turtle
    # and a golden pheasant) and the ties have been broken with off-book forms.
    #
    # Guarded on binomials for the same reason as the concatenated form: a
    # trinomial's 4+4 is built from its parent's genus and species, so
    # "Strix occidentalis caurina" would otherwise claim "StriOcci".
    long_prefix = _make_long_prefix(latin_name)
    if (
        long_prefix
        and len(scientific_parts) == 2
        and _GENERATED_LONG_PREFIX_COUNTS[long_prefix] == 1
    ):
        results.append(long_prefix)

    deduped = []
    seen = set()
    for alias in results:
        if alias not in seen:
            deduped.append(alias)
            seen.add(alias)
    return deduped


def _decorated_scientific_name_candidates(name):
    """
    Extract decreasing scientific-name prefixes from decorated scientific names
    such as "Cyprinus carpio 'xingguonensis'", "Canis lupus familiaris", or
    "Strix occidentalis caurina (northern spotted owl)".

    Returns a list ordered from the longest scientific prefix to the shortest
    valid fallback. Exact full-name matches are omitted because callers try
    those before using this helper.
    """
    parts = name.split()
    if len(parts) < 3:
        return []

    genus = parts[0]
    if not re.fullmatch(r"[A-Z][a-z]+", genus):
        return []

    scientific_parts = [genus]
    for part in parts[1:]:
        if re.fullmatch(r"(?:[a-z][a-z-]*|sp\.)", part):
            scientific_parts.append(part)
        else:
            break

    if len(scientific_parts) < 2:
        return []

    candidates = []
    for length in range(len(scientific_parts), 1, -1):
        candidate = " ".join(scientific_parts[:length])
        if candidate != name:
            candidates.append(candidate)
    return candidates


def _normalize_identifier(value):
    """Strip punctuation and case so two spellings of a prefix compare equal."""
    return re.sub(r"[^A-Za-z0-9]+", "", value).lower()


def _prefix_is_derived_from_name(prefix, latin_name):
    """
    Is this entry's prefix just a normalization of its own name?

    Used to decide whether a group node hands its prefix down to descendants.
    "Galliformes sp." carries the prefix "Galliformes" and "NHP" carries "NHP";
    neither is a published designation, so neither becomes a child's inherited
    old MHC prefix. "Bos sp." carries "BoLA", which is not derived from the
    name and is a real designation, so Bos taurus inherits it.

    Note what this does NOT establish. It is a string test, not a claim about
    nomenclature: "NHP" passes it and is a paraphyletic database section rather
    than a taxon, and a species whose curated prefix happens to equal its own
    concatenated binomial ("Bubo bubo" -> "BuboBubo") would pass it too. That
    second case is why _is_group_entry is required -- see the caller.
    """
    latin_parts = [part for part in latin_name.split() if part.lower() != "sp."]
    if not latin_parts:
        return False
    return _normalize_identifier(prefix) in {
        _normalize_identifier(latin_parts[0]),
        "".join(_normalize_identifier(part) for part in latin_parts),
    }


def _is_group_entry(latin_name):
    """
    Does this entry stand for a group of species rather than one species?

    Most group entries announce themselves by being written "<taxon> sp.". One
    cannot: "NHP" is IPD-MHC's section for non-human primates and is not a
    taxon at all (#122), so it declares "group: true" instead. Any future
    database section that is not a clade does the same, rather than being
    hardcoded here (#135).

    Group-ness alone decides nothing; it is one half of both tests that use it.
    A prefix is suppressed rather than inherited, and reports provenance
    "group label", only when the entry is a group *and* the prefix is merely
    its own name. A group entry carrying a real designation is unaffected:
    "Bos sp." reports "designated" and hands "BoLA" down.
    """
    if raw_species_dict.get(latin_name, {}).get("group"):
        return True
    return latin_name.endswith(" sp.")


# How an entry came by its prefix. "designated" means it is published
# nomenclature -- IPD-MHC or IMGT/HLA writes alleles with it. "generated" means
# mhcgnomes derived it from the latin name. "group label" means it names a
# grouping rather than a species and is never written on an allele. None means
# nobody has established which, and that is deliberately distinguishable from
# "designated": a prefix that mhcgnomes did not generate is not thereby proven
# to be in published use. See issue #128 and the Caau case in AGENTS.md.
PREFIX_PROVENANCE_VALUES = frozenset({"designated", "generated", "group label"})


def _is_inheritable_umbrella(prefix, latin_name):
    """
    Does this entry hand its prefix down to descendants as their old prefix?

    True for anything carrying a prefix that is not simply its own name, which
    covers real designations ("Bos sp." with "BoLA", "Mus sp." with "MusSp")
    and every ordinary species. False only for a group entry labelled with its
    own taxon: "Aves sp." with "Aves", "NHP" with "NHP".

    The group-entry requirement is what fixes the tautonym case. "Bubo bubo"
    carries "BuboBubo", which *is* derived from its name, but it is one species
    rather than a grouping, so a subspecies parented under it should inherit
    the prefix the way any other child does.
    """
    return not (_is_group_entry(latin_name) and _prefix_is_derived_from_name(prefix, latin_name))


def prefix_is_derived_for(prefix, latin_name):
    """
    Would mhcgnomes mint this prefix for that species from its latin name?

    True for the concatenated binomial and for the 4+4 shorthand, whether or
    not the emitter actually offers it -- a colliding 4+4 is withheld but is
    still *derivable*, which is exactly what makes it contested. Used to keep
    error messages from calling a derived form "source-attested".
    """
    normalized = _normalize_identifier(prefix)
    for generator in (_make_full_scientific_prefix, _make_long_prefix):
        generated = generator(latin_name)
        if generated and _normalize_identifier(generated) == normalized:
            return True
    return False


def unambiguous_prefix_for(species):
    """
    A prefix that names this species and nothing else.

    The concatenated binomial where there is one -- it is the only form with no
    collisions anywhere in the ontology -- otherwise the curated prefix. Do not
    offer `species.prefix` blindly: "Chpi" is Chrysolophus pictus's canonical
    prefix and is derivable by Klein's 2+2 rule from Chrysemys picta too, so
    recommending it in a collision message just moves the collision.
    """
    full = _make_full_scientific_prefix(species.name)
    if full and len(_scientific_name_parts(species.name)) == 2:
        return full
    return species.prefix


def _derive_prefix_provenance(prefix, latin_name):
    """
    What can be established about a prefix without consulting a source.

    Only two answers are provable: a group entry whose prefix is its own name is
    a label, and a prefix this entry would actually be given by the alias
    generator is one we minted. The second asks the emitter rather than the
    generator functions, so a form the emitter declines -- a colliding 4+4, or
    anything on a trinomial -- is not claimed as ours. Everything else returns
    None so that a curator has to look it up rather than inherit a guess.
    """
    if not _is_inheritable_umbrella(prefix, latin_name):
        return "group label"
    normalized = prefix.lower()
    if any(
        alias.lower() == normalized for alias in _auto_generated_prefixes_for_latin_name(latin_name)
    ):
        return "generated"
    return None


_EMPTY_GENE_NAMES = NormalizingSet()

# Populated as a side effect of create_species_for_latin_name, which is cached
# and so runs its gene walk exactly once per species. Fully built by the time
# create_species_lookup_dictionaries() below has visited every latin name.
latin_name_to_own_gene_names = {}


# Every key an entry in species.yaml may carry, and every one of them is read
# below. Unknown keys are rejected rather than ignored: a typo such as
# "prefix_source" would otherwise load silently, leaving the YAML asserting
# something the runtime never read. Whitelisting a key nothing reads has the
# same effect with extra confidence, so do not add one here without a consumer
# -- tests/test_ontology_hygiene.py checks that each key has one (#139).
SPECIES_ENTRY_KEYS = frozenset(
    {
        "context only prefixes",
        "gene families",
        "gene properties",
        "genes",
        "group",
        "name",
        "old prefix",
        "other prefixes",
        "parent",
        "prefix",
        "prefix source",
    }
)


@cache
def create_species_for_latin_name(latin_name):
    if latin_name not in raw_species_dict:
        raise ValueError(f"Species not found: '{latin_name}'")
    species_info = raw_species_dict[latin_name]
    unknown_keys = sorted(set(species_info) - SPECIES_ENTRY_KEYS)
    if unknown_keys:
        raise ValueError(
            f"Unknown key(s) {unknown_keys} in the '{latin_name}' entry of the species "
            f"ontology; expected one of {sorted(SPECIES_ENTRY_KEYS)}"
        )
    parent_species_latin_name = species_info.get("parent")
    if not parent_species_latin_name and latin_name != "Gnathostomata sp.":
        # Default: all species descend from the jawed-vertebrate root
        parent_species_latin_name = "Gnathostomata sp."
    if parent_species_latin_name:
        parent_species = create_species_for_latin_name(parent_species_latin_name)
    else:
        parent_species = None

    prefix = species_info.get("prefix")
    if not prefix:
        raise ValueError(f"Missing 'prefix' for '{latin_name}' in species ontology")

    group_flag = species_info.get("group")
    if group_flag is not None and group_flag is not True:
        raise ValueError(
            f"'group' of '{latin_name}' is {group_flag!r}; the only accepted value is true. "
            f"Omit the key for an ordinary species."
        )

    prefix_provenance = species_info.get("prefix source")
    if prefix_provenance is not None and (
        not isinstance(prefix_provenance, str) or prefix_provenance not in PREFIX_PROVENANCE_VALUES
    ):
        raise ValueError(
            f"'prefix source' of '{latin_name}' is {prefix_provenance!r}, "
            f"expected one of {sorted(PREFIX_PROVENANCE_VALUES)}"
        )
    if prefix_provenance is None:
        prefix_provenance = _derive_prefix_provenance(prefix, latin_name)

    old_mhc_prefix = species_info.get("old prefix")
    if not old_mhc_prefix and parent_species:
        parent_prefix = parent_species.prefix
        if _is_inheritable_umbrella(parent_prefix, parent_species.name):
            old_mhc_prefix = parent_prefix

    other_mhc_prefixes = species_info.get("other prefixes")
    if type(other_mhc_prefixes) is str:
        other_mhc_prefixes = [other_mhc_prefixes]
    elif other_mhc_prefixes is None:
        other_mhc_prefixes = []

    context_only_mhc_prefixes = species_info.get("context only prefixes")
    if type(context_only_mhc_prefixes) is str:
        context_only_mhc_prefixes = [context_only_mhc_prefixes]
    elif context_only_mhc_prefixes is None:
        context_only_mhc_prefixes = []

    # Prefix spellings attested in an external database or the literature,
    # from evidenced_prefix_aliases.yaml. Whether each is globally parseable or
    # context-only was decided by _partition_evidenced_aliases from how many
    # species claim it -- see issue #136.
    for alias in EVIDENCED_GLOBAL_ALIASES.get(latin_name, ()):
        if alias and alias != prefix and alias not in other_mhc_prefixes:
            other_mhc_prefixes = [*list(other_mhc_prefixes), alias]
    for alias in EVIDENCED_CONTEXT_ONLY_ALIASES.get(latin_name, ()):
        if alias and alias != prefix and alias not in context_only_mhc_prefixes:
            context_only_mhc_prefixes = [*list(context_only_mhc_prefixes), alias]

    # Auto-generate parseable aliases from the latin name, for binomials only:
    # 1. The full concatenated scientific name, which is the default and is
    #    collision-free across the ontology.
    # 2. A 4+4 shorthand, only when it is globally unique.
    # Trinomial entries mint neither, so a subspecies never claims a name
    # derived from its parent binomial.
    for alias in _auto_generated_prefixes_for_latin_name(latin_name):
        if alias and alias != prefix and alias not in other_mhc_prefixes:
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
        gene_name_to_properties = NormalizingDictionary()
        gene_family_name_to_gene_names = NormalizingDictionary()
        class2_loci = NormalizingSet()
        class2_locus_to_gene_names = NormalizingDictionary(default_value_fn=set)
        class2_gene_name_to_chain_type = NormalizingDictionary()
    else:
        gene_names = parent_species.gene_names.copy()
        gene_name_to_mhc_class = parent_species.gene_name_to_mhc_class.copy()
        gene_name_to_properties = parent_species.gene_name_to_properties.map_values(dict)
        gene_family_name_to_gene_names = parent_species.gene_family_name_to_gene_names.map_values(
            _ensure_normalizing_set
        )
        class2_loci = parent_species.class2_loci.copy()
        class2_locus_to_gene_names = parent_species.class2_locus_to_gene_names.map_values(set)
        class2_gene_name_to_chain_type = parent_species.class2_gene_name_to_chain_type.copy()

    # Genes this entry declares itself, as opposed to the ones it inherited
    # from parent_species above. Collected inside the same validated walk so it
    # cannot drift from gene_names: it sees exactly the class keys the loader
    # accepts, and normalizes names the same way.
    own_gene_names = NormalizingSet()

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
                own_gene_names.add(str(gene_name))
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
                    own_gene_names.add(gene_name)
                    gene_name_to_mhc_class[gene_name] = mhc_class
                    class2_locus_to_gene_names[locus].add(gene_name)
                    # TODO:
                    #  make alpha vs. beta chain genes explicit in
                    #  the YAML file ontology
                    chain_type = guess_class2_chain_type(gene_name)
                    class2_gene_name_to_chain_type[gene_name] = chain_type

    latin_name_to_own_gene_names[latin_name] = own_gene_names

    raw_gene_properties = species_info.get("gene properties", {})
    if not isinstance(raw_gene_properties, dict):
        raise ValueError(f"Malformed gene properties for '{latin_name}'")
    for raw_gene_name, raw_properties in raw_gene_properties.items():
        canonical_gene_name = gene_names.get_original(raw_gene_name)
        if canonical_gene_name is None:
            raise ValueError(
                f"Gene properties for '{latin_name}' reference unknown gene '{raw_gene_name}'"
            )
        if not isinstance(raw_properties, dict):
            raise ValueError(
                f"Malformed properties for gene '{canonical_gene_name}' of '{latin_name}'"
            )
        unexpected_properties = set(raw_properties).difference(
            {"pseudogene", "alleles", "context only"}
        )
        if unexpected_properties:
            raise ValueError(
                f"Unknown properties for gene '{canonical_gene_name}' of '{latin_name}': "
                f"{sorted(unexpected_properties)}"
            )
        if "pseudogene" in raw_properties and type(raw_properties["pseudogene"]) is not bool:
            raise ValueError(
                f"Pseudogene status for gene '{canonical_gene_name}' of '{latin_name}' "
                "must be boolean"
            )
        if "alleles" in raw_properties and raw_properties["alleles"] != "none":
            raise ValueError(
                f"'alleles' for gene '{canonical_gene_name}' of '{latin_name}' is "
                f"{raw_properties['alleles']!r}; the only accepted value is 'none'"
            )
        if "context only" in raw_properties and type(raw_properties["context only"]) is not bool:
            raise ValueError(
                f"'context only' for gene '{canonical_gene_name}' of '{latin_name}' must be boolean"
            )
        combined_properties = dict(gene_name_to_properties.get(canonical_gene_name, {}))
        combined_properties.update(raw_properties)
        gene_name_to_properties[canonical_gene_name] = combined_properties

    raw_gene_families = species_info.get("gene families", {})
    if not isinstance(raw_gene_families, dict):
        raise ValueError(f"Malformed gene families for '{latin_name}'")
    for raw_family_name, raw_family_members in raw_gene_families.items():
        if not isinstance(raw_family_members, list) or not raw_family_members:
            raise ValueError(
                f"Gene family '{raw_family_name}' of '{latin_name}' must be a non-empty list"
            )
        if raw_family_name in gene_names:
            raise ValueError(
                f"Gene family '{raw_family_name}' of '{latin_name}' conflicts with a gene name"
            )
        canonical_members = NormalizingSet()
        member_classes = set()
        for raw_member_name in raw_family_members:
            canonical_member_name = gene_names.get_original(raw_member_name)
            if canonical_member_name is None:
                raise ValueError(
                    f"Gene family '{raw_family_name}' of '{latin_name}' references unknown gene "
                    f"'{raw_member_name}'"
                )
            canonical_members.add(canonical_member_name)
            member_classes.add(gene_name_to_mhc_class[canonical_member_name])
        if len(member_classes) != 1:
            raise ValueError(
                f"Gene family '{raw_family_name}' of '{latin_name}' spans MHC classes "
                f"{sorted(member_classes)}"
            )
        gene_family_name_to_gene_names[str(raw_family_name)] = canonical_members

    # Revalidate inherited families against the descendant's effective gene
    # ontology. A descendant may reclassify a gene, but a family classification
    # is only valid when all exact members still share one class.
    for family_name, family_members in gene_family_name_to_gene_names.items():
        if family_name in gene_names:
            raise ValueError(
                f"Gene family '{family_name}' of '{latin_name}' conflicts with a gene name"
            )
        member_classes = {gene_name_to_mhc_class.get(member) for member in family_members}
        if None in member_classes:
            raise ValueError(
                f"Gene family '{family_name}' of '{latin_name}' references an unknown gene"
            )
        if len(member_classes) != 1:
            raise ValueError(
                f"Gene family '{family_name}' of '{latin_name}' spans MHC classes "
                f"{sorted(member_classes)}"
            )

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
        gene_name_to_properties=gene_name_to_properties,
        gene_family_name_to_gene_names=gene_family_name_to_gene_names,
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
        context_only_mhc_prefixes=context_only_mhc_prefixes,
        other_common_names=[name for name in common_names if name != shortest_common_name],
        prefix_provenance=prefix_provenance,
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
    context_only_alias_to_species_objects = NormalizingDictionary(default_value_fn=set)

    for latin_name in raw_species_dict:
        species = create_species_for_latin_name(latin_name)
        latin_name_to_species[latin_name] = species
        species_name_to_species[latin_name] = species
        for s in species.all_identifiers:
            alias_to_species_objects[s].add(species)
        for s in species.context_only_mhc_prefixes:
            context_only_alias_to_species_objects[s].add(species)
        for gene_name in species.gene_names_and_aliases:
            gene_name_to_species_objects[gene_name].add(species)

    return (
        latin_name_to_species,
        species_name_to_species,
        alias_to_species_objects,
        context_only_alias_to_species_objects,
        gene_name_to_species_objects,
    )


(
    latin_name_to_species_object,
    species_name_to_species_object,
    alias_to_species_objects,
    context_only_alias_to_species_objects,
    gene_name_to_species_objects,
) = create_species_lookup_dictionaries()


def species_named_in(name):
    """
    Which species, if any, the string names outright.

    Covers both routes the parser uses to take a species off the front of a
    string, since neither alone is enough:

      - an attached prefix, as in "Gaga-BLB2*02" or "H2-Kb", which tokenizes
        as a single token
      - leading species tokens, as in "mouse H2-Kb" or "Homo sapiens class I"

    so that all of those count as naming their species while "BLB2*02" and
    "class II" do not. Callers compare a result's own species against this
    list, so an over-eager prefix match on a string that names no species is
    harmless. Returns a possibly empty list.
    """
    from .tokenize import tokenize

    matches = []

    species_from_prefix = infer_species_from_prefix(name)
    # The second element is the part of the string that matched. It is empty
    # when infer_species_from_prefix fell through to its last resort and
    # inferred the species from a gene name unique to one entry, which is the
    # opposite of naming it: "A8*01:01" reported its species as explicit, so
    # require_explicit_species accepted a string that names no species at all.
    # 98 gene names took that route. See issue #130.
    if species_from_prefix is not None and species_from_prefix[1]:
        matches.append(species_from_prefix[0])

    tokenization_result = tokenize(name)
    tokens = tokenization_result.tokens
    for num_species_tokens in [3, 2, 1]:
        if len(tokens) >= num_species_tokens:
            query = " ".join([t.seq for t in tokens[:num_species_tokens]])
            token_matches = find_matching_species_objects(query)
            if token_matches:
                matches.extend(token_matches)
                break

    attributes = tokenization_result.attributes
    for key in ("OS", "species"):
        if key in attributes:
            from_attributes = Species.get(attributes[key])
            if from_attributes is not None:
                matches.append(from_attributes)
            break
    return matches


def classify_species_source(name, species, default_species):
    """
    Returns "explicit", "inferred", "default" or None for how `species` came to
    be associated with the string `name`. See Result.species_source.
    """
    if species is None:
        return None
    if species in species_named_in(name):
        return "explicit"
    if default_species is not None and species == Species.get(default_species):
        return "default"
    return "inferred"


def find_matching_species_objects(name):
    """
    Returns list of Species
    """
    if type(name) is Species:
        return [name]
    if name is None:
        return []
    return list(alias_to_species_objects.get(name, []))


def find_matching_context_only_species_objects(name):
    """
    Returns list of Species for prefixes that are intentionally accepted only
    when additional species context is supplied by the caller.
    """
    if type(name) is Species:
        return [name]
    if name is None:
        return []
    return list(context_only_alias_to_species_objects.get(name, []))


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


def _candidate_prefix_substrings(name):
    candidates = [name]
    if "-" in name or "." in name:
        parts_split_by_separator = re.split(r"[-.]", name)
        first = parts_split_by_separator[0]
        if first not in candidates:
            candidates.append(first)
        if len(parts_split_by_separator) > 1:
            first_two = parts_split_by_separator[0] + "-" + parts_split_by_separator[1]
            if first_two not in candidates:
                candidates.append(first_two)
    return candidates


def _sort_species_by_ontology_order(species_objects):
    return sorted(species_objects, key=lambda sp: _RAW_SPECIES_ORDER.get(sp.name, float("inf")))


def infer_species_from_context_only_prefix(name, _allow_mhc_strip=True):
    """
    Find source-attested but globally blocked species prefixes such as Hymo,
    Moal, or Orla. Returns a tuple of:
        - matching Species objects
        - the original prefix substring that matched

    Unlike infer_species_from_prefix, this function does not choose a global
    winner or use gene-context disambiguation. It exists to support
    species-constrained reparsing and informative conflict errors.
    """
    if _allow_mhc_strip and "-" in name:
        prefix_part, rest = name.split("-", 1)
        if len(prefix_part) > 3 and prefix_part[-3:].upper() == "MHC":
            stripped_name = prefix_part[:-3] + "-" + rest
            result = infer_species_from_context_only_prefix(stripped_name, _allow_mhc_strip=False)
            if result is not None:
                species_objects, _ = result
                return species_objects, prefix_part

    candidate_species_substrings = _candidate_prefix_substrings(name)
    for num_chars in [None, 4, 3, 2]:
        for candidate in candidate_species_substrings:
            original_prefix = candidate[:num_chars] if num_chars else candidate
            species_objects = find_matching_context_only_species_objects(original_prefix)
            if species_objects:
                return tuple(_sort_species_by_ontology_order(species_objects)), original_prefix

    if _allow_mhc_strip and len(name) > 3 and name[:3].lower() == "mhc":
        stripped = name[3:]
        result = infer_species_from_context_only_prefix(stripped, _allow_mhc_strip=False)
        if result is not None:
            species_objects, inner_prefix = result
            return species_objects, name[: 3 + len(inner_prefix)]

    return None


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
    # Strip a trailing "MHC" suffix on the species prefix portion before
    # normal prefix scanning. Common in bird/bat literature, e.g.:
    #   "ManaMHC-DAB*01" → "Mana-DAB*01"
    #   "MaerMHC-UA*01"  → "Maer-UA*01"
    # Must run first so the base prefix ("Mana") is found by normal scanning
    # instead of matching and leaving "MHC-DAB*01" as an unparseable remainder.
    if _allow_mhc_strip and "-" in name:
        prefix_part, rest = name.split("-", 1)
        if len(prefix_part) > 3 and prefix_part[-3:].upper() == "MHC":
            stripped_name = prefix_part[:-3] + "-" + rest
            result = infer_species_from_prefix(stripped_name, _allow_mhc_strip=False)
            if result is not None:
                species_object, inner_prefix = result
                # Return the full original prefix (with MHC suffix) so the
                # caller correctly computes the remaining string.
                return species_object, prefix_part

    # Try parsing a few different substrings to get the species,
    # and then use the species gene list to determine what the gene is in this string
    candidate_species_substrings = _candidate_prefix_substrings(name)

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
