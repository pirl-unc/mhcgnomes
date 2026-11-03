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

from os.path import dirname, join

import yaml

from .common import normalize_allele_alias
from .normalizing_dictionary import NormalizingDictionary

package_dir = dirname(__file__)
data_dir = join(package_dir, "data")


def get_path(yaml_filename):
    """
    Path of a file in the packaged ``mhcgnomes/data`` directory.

    Parameters
    ----------
    yaml_filename : str
        File name inside the data directory, e.g. "species.yaml".

    Returns
    -------
    str
        Absolute path to the file. Its existence is not checked.
    """
    return join(data_dir, yaml_filename)


def load(yaml_filename, normalize_first_level_keys=False, normalize_second_level_keys=False):
    """
    Load a packaged YAML data file, optionally with normalized keys.

    Every runtime table in this module (species, aliases, haplotypes,
    serotypes, ...) is read through this function once, at import time.

    Parameters
    ----------
    yaml_filename : str
        File name inside the data directory, e.g. "haplotypes.yaml".
    normalize_first_level_keys : bool
        Wrap the top-level mapping in a NormalizingDictionary, so lookups by
        species prefix ignore case and punctuation.
    normalize_second_level_keys : bool
        Wrap each top-level value in a NormalizingDictionary, so lookups by
        gene, allele, haplotype or serotype name do the same. Requires every
        top-level value to be a mapping.

    Returns
    -------
    object
        The parsed YAML (usually a dict), with the requested levels converted
        to NormalizingDictionary.

    Raises
    ------
    OSError
        If the file cannot be opened.
    yaml.YAMLError
        If the file is not valid YAML.
    """
    path = get_path(yaml_filename)
    with open(path, encoding="utf-8") as f:
        result = yaml.safe_load(f)

    if normalize_second_level_keys:
        # turn first layer of values in dictionary into NormalizingDictionary
        result = {k: NormalizingDictionary.from_dict(v) for (k, v) in result.items()}

    if normalize_first_level_keys:
        result = NormalizingDictionary.from_dict(result)

    return result


# dictionary mapping scientific name -> info dictionary
species = load("species.yaml")

# species -> [{alias, status, evidence}], attested prefix spellings imported
# from the mhcseqs registry. Kept out of species.yaml because provenance here
# is per (species, alias) rather than per species. See issue #136.
evidenced_prefix_aliases = load("evidenced_prefix_aliases.yaml")

# Curation holding area: source signal not yet stable enough for runtime. Read
# so the evidenced-alias import cannot override a deliberate holdback (#136).
underrepresented_taxa_source_registry = load("underrepresented_taxa_source_registry.yaml")

# Dictionary mapping each species prefix to a dictionary from old gene
# names to new ones
gene_aliases = load(
    "gene_aliases.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping each species prefix to a dictionary from
# old/retired/provisional allele names to standard new names
allele_aliases = NormalizingDictionary.from_dict(
    {
        prefix: NormalizingDictionary.from_dict(aliases, normalize_fn=normalize_allele_alias)
        for prefix, aliases in load("allele_aliases.yaml").items()
    }
)

# Curated minimum width of the first allele field, keyed by species and gene.
# These entries override widths inferred from canonical allele-alias targets.
first_allele_field_widths = load("first_allele_field_widths.yaml")

# Dictionary mapping species -> gene -> list of known allele names
known_alleles = load(
    "known_alleles.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping species to haplotype name to list of alleles
haplotypes = load(
    "haplotypes.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping species to serotype name to list of alleles
serotypes = load(
    "serotypes.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping species to heterodimer shorthand to alpha/beta allele pairs
# e.g., HLA -> DQ2.5 -> {alpha: DQA1*05:01, beta: DQB1*02:01}
heterodimers = load(
    "heterodimers.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping species to supertype name to supertype info
# e.g., HLA -> A02 -> {representative: A*02:01, alleles: [A*02:01, A*02:02, ...]}
# Supertypes are functional groupings based on peptide-binding specificity
# (Sidney et al. 2008, https://pmc.ncbi.nlm.nih.gov/articles/PMC2245908/)
supertypes = load(
    "supertypes.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Complete allele names whose only field is numeric (HLA-MICA*001, Papa-B*03),
# generated from the pinned IMGT/HLA and IPD-MHC releases by
# scripts/generate_single_field_alleles.py. Read by Allele.is_allele_group.
single_field_alleles = load("single_field_alleles.yaml")


# Normalization is a compatibility policy independent of optional alias data.
min_first_field_widths = {
    (prefix, str(gene)): int(width)
    for prefix, genes in first_allele_field_widths.items()
    for gene, width in genes.items()
}

# Sparse exact-current-name guards for alias lookup; not a registry catalog.
current_allele_names = {
    prefix: frozenset(normalize_allele_alias(name) for name in names)
    for prefix, names in load("current_allele_names.yaml").items()
}
