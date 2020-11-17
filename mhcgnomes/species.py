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

from collections import OrderedDict, defaultdict
from typing import Union, Mapping, Iterable

from .common import cache
from .data import gene_aliases as raw_gene_aliases_dict
from .data import serotypes as raw_serotypes_dict
from .data import haplotypes as raw_haplotypes_dict
from .data import allele_aliases as raw_allele_aliases_dict
from .data import species as raw_species_dict
from .mhc_class_helpers import class1_restrictions, class2_restrictions
from .normalizing_set import NormalizingSet
from .normalizing_dictionary import NormalizingDictionary
from .result import Result

class Species(Result):
    """
    Representation of a parsed species prefix such as "HLA", "ELA"
    """
    def __init__(
            self,
            name : str,
            common_name : str,
            mhc_prefix : str,
            gene_names : Iterable[str],
            gene_name_to_mhc_class : Mapping[str, str],
            class2_loci : Iterable[str],
            class2_locus_to_gene_names : Mapping[str, Iterable[str]],
            class2_gene_name_to_chain_type : Mapping[str, str],
            gene_aliases : Mapping[str, str],
            allele_aliases : Mapping[str, str],
            haplotypes : Mapping[str, Iterable[str]],
            serotypes : Mapping[str, Iterable[str]],
            parent_species : Union['Species', None] = None,
            old_mhc_prefix: Union[str, None] = None,
            other_mhc_prefixes : Iterable[str] = [],
            other_common_names : Iterable[str] = [],
            taxon_id: Union[int, None] = None,
            raw_string : Union[str, None] = None):
        Result.__init__(self, raw_string=raw_string)
        self.name = name
        self.common_name = common_name
        self.other_common_names = list(other_common_names)
        self.mhc_prefix = mhc_prefix
        self.other_mhc_prefixes = set(other_mhc_prefixes)
        if old_mhc_prefix:
            self.old_mhc_prefix = old_mhc_prefix
        else:
            self.old_mhc_prefix = mhc_prefix

        self.taxon_id = taxon_id
        self.gene_names = gene_names
        self.gene_name_to_mhc_class = gene_name_to_mhc_class
        self.class2_loci = class2_loci
        self.class2_locus_to_gene_names = class2_locus_to_gene_names
        self.class2_gene_name_to_chain_type = class2_gene_name_to_chain_type
        self.gene_aliases = gene_aliases
        # create a reverse lookup from proper names to their list of aliases
        self.reverse_gene_aliases = \
            self._create_reverse_gene_aliases(gene_names, gene_aliases)

        self.allele_aliases = allele_aliases
        self.haplotypes = haplotypes
        self.serotypes = serotypes
        self.parent_species = parent_species

    @classmethod
    def _create_reverse_gene_aliases(cls, gene_names, gene_aliases):
        """
        Creates dictionary mapping canonical gene name to its set of aliases.
        """
        d = defaultdict(set)

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
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)

    @classmethod
    @cache
    def get_multiple(cls, species_name):
        """
        Cached wrapper around find_matching_species which tries to
        identify one or more species from any of its scientific name,
        common names, MHC prefixes.
        """
        return find_matching_species_objects(species_name)

    @classmethod
    @cache
    def get(cls, species_name):
        if type(species_name) is Species:
            return species_name
        elif type(species_name) is not str:
            return None

        species_objects = cls.get_multiple(species_name)
        if len(species_objects) == 0:
            return None
        # sort species by how well their prefix or name matches the given query
        # and how many genes they have a species with more curated genes
        # is more likely to be the one we're looking for in case of an
        # ambiguous MHC prefix
        return sorted(
            species_objects,
            key=create_species_sort_key(species_name))[-1]

    def to_record(self):
        return OrderedDict([
            ("species_prefix", self.prefix),
            ("species_name", self.name),
        ])

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
        if self.old_mhc_prefix:
            prefixes.add(self.old_mhc_prefix)
        return [self.prefix] + sorted(prefixes)

    @property
    def all_common_names(self):
        """
        Returns all common names used for this species
        """
        return [self.common_name] + self.other_common_names

    @property
    def all_identifiers(self):
       """
       Return all names and prefixes associated with this Species.

       Returns list of str
       """
       return [self.name] + self.all_mhc_prefixes + self.all_common_names

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
    while trimmed_gene_name[-1].isdigit():
        trimmed_gene_name = trimmed_gene_name[:-1]
    last_letter = trimmed_gene_name[-1].upper()
    is_alpha = (last_letter == "A")
    # assume that anything which can't be pinned down to be an alpha chain
    # is then a beta chain, since more of the variability/gene copying
    # seems to occur in beta chains
    return ("alpha" if is_alpha else "beta")

@cache
def create_species_for_latin_name(latin_name):
    if latin_name not in raw_species_dict:
        raise ValueError("Species not found: '%s'" % (latin_name,))
    species_info = raw_species_dict[latin_name]
    parent_species_latin_name = species_info.get("parent")
    if parent_species_latin_name:
        parent_species = create_species_for_latin_name(parent_species_latin_name)
    else:
        parent_species = None

    prefix = species_info.get("prefix")
    if not prefix:
        raise ValueError(
            "Missing 'prefix' for '%s' in species ontology" % (latin_name,))

    old_mhc_prefix = species_info.get("old prefix")
    if not old_mhc_prefix:
        if parent_species:
            old_mhc_prefix = parent_species.prefix

    other_mhc_prefixes = species_info.get("other prefixes")
    if type(other_mhc_prefixes) is str:
        other_mhc_prefixes = [other_mhc_prefixes]
    elif other_mhc_prefixes is None:
        other_mhc_prefixes = []

    common_name = species_info.get("name")
    if not common_name:
        raise ValueError(
            "Missing 'name' for '%s' in species ontology" % (latin_name,))

    if type(common_name) is str:
        common_names = [common_name]
    else:
        common_names = common_name
    # make all common names lowercase
    common_names = [s.lower() for s in common_names]
    shortest_common_name = min(common_names, key=len)

    taxon_id = species_info.get("taxon")
    if type(taxon_id) is str:
        taxon_id = int(taxon_id)


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
        class2_locus_to_gene_names = parent_species.class2_locus_to_gene_names.copy()
        class2_gene_name_to_chain_type = parent_species.class2_gene_name_to_chain_type.copy()

    for mhc_class, mhc_class_members in species_info.get("genes", {}).items():
        if mhc_class_members is None:
            raise ValueError("Unexpected None in gene ontology for class '%s' of '%s'" % (
                mhc_class,
                latin_name))
        if mhc_class in class1_restrictions.union({"other"}):
            if type(mhc_class_members) is not list:
                raise ValueError(
                    "Malformed gene ontology for '%s' MHC class '%s'" % (
                        latin_name, mhc_class))
            for gene_name in mhc_class_members:
                gene_names.add(str(gene_name))
                gene_name_to_mhc_class[gene_name] = mhc_class
        elif mhc_class in class2_restrictions:
            if type(mhc_class_members) is not dict:
                raise ValueError(
                    "Malformed gene ontology for '%s' MHC class '%s'" % (
                        latin_name, mhc_class))
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

    if parent_species is None:
        all_identifiers = []
    else:
        all_identifiers = list(parent_species.all_identifiers)
    all_identifiers.append(latin_name)
    all_identifiers.append(prefix)
    all_identifiers.extend(other_mhc_prefixes)
    all_identifiers.extend(common_names)

    # Don't rely on other YAML files to use any particular prefix or
    # species identifier, just try them all
    # One reason for this is that canonical species prefixes might change
    # over time and don't want one update to break code mysteriously
    # elsewhere. Another reason is that a few species share the same
    # prefix ('Bubu' belongs to both an owl species and water buffalo).
    gene_aliases = combine_matching_keys(
        raw_gene_aliases_dict,
        all_identifiers)
    allele_aliases = combine_matching_keys(
        raw_allele_aliases_dict,
        all_identifiers)
    haplotypes = combine_matching_keys(
        raw_haplotypes_dict,
        all_identifiers)
    serotypes = combine_matching_keys(
        raw_serotypes_dict,
        all_identifiers)
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
        haplotypes=haplotypes,
        serotypes=serotypes,
        other_mhc_prefixes=other_mhc_prefixes,
        other_common_names=[
            name for name in common_names
            if name != shortest_common_name],
        taxon_id=taxon_id,
        raw_string=latin_name)

def combine_matching_keys(d, keys, dictionary_class=NormalizingDictionary):
    result = dictionary_class()
    for key in keys:
        if key in d:
            sub_dict = dictionary_class.from_dict(d[key])
            result.update(sub_dict)
    return result

def create_species_lookup_dictionaries():
    gene_name_to_species_objects = NormalizingDictionary(default_value_fn=set)
    species_name_to_species_object = NormalizingDictionary()

    # latin name, common names, or MHC prefixes all mapping to multiple
    # species objects
    alias_to_species_objects = NormalizingDictionary(default_value_fn=set)

    for latin_name in raw_species_dict.keys():
        species = create_species_for_latin_name(latin_name)
        species_name_to_species_object[latin_name] = species
        for s in species.all_identifiers:
            alias_to_species_objects[s].add(species)
        for gene_name in species.gene_names_and_aliases:
            gene_name_to_species_objects[gene_name].add(species)
    return (
        species_name_to_species_object,
        alias_to_species_objects,
        gene_name_to_species_objects)

species_name_to_species_object, alias_to_species_objects, gene_name_to_species_objects = \
    create_species_lookup_dictionaries()

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
        same_prefix = (species.prefix == query_string)
        similar_prefix = (
            species.prefix.lower().strip() ==
            query_string.lower().strip())
        num_genes = species.num_genes
        return (same_prefix, similar_prefix, num_genes)
    return sort_key

def infer_species_from_prefix(name):
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
    candidate_species_substrings = {
        name,
        # sometimes alleles are preceded by a space 'HLA A*02:01'
        name.split()[0],
    }

    for candidate in list(candidate_species_substrings):
        if "-" in candidate:
            # if name is "H-2-K" then try parsing "H" and "H-2" as a species
            # prefix
            parts_split_by_dash = name.split("-")
            candidate_species_substrings.update([
                parts_split_by_dash[0],
                parts_split_by_dash[0] + "-" + parts_split_by_dash[1]
            ])

    for num_chars in [None, 4, 3, 2]:
        for candidate in candidate_species_substrings:
            if num_chars:
                original_prefix = candidate[:num_chars]
            else:
                original_prefix = candidate
            species_objects = find_matching_species_objects(original_prefix)
            if species_objects:
                species = sorted(
                    species_objects,
                    key=create_species_sort_key(original_prefix))[-1]
                return species, original_prefix

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



