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

from .normalizing_dictionary import NormalizingDictionary

package_dir = dirname(__file__)
data_dir = join(package_dir, "data")


def get_path(yaml_filename):
    return join(data_dir, yaml_filename)


def load(yaml_filename, normalize_first_level_keys=False, normalize_second_level_keys=False):
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

# Dictionary mapping each species prefix to a dictionary from old gene
# names to new ones
gene_aliases = load(
    "gene_aliases.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
)

# Dictionary mapping each species prefix to a dictionary from
# old/retired/provisional allele names to standard new names
allele_aliases = load(
    "allele_aliases.yaml", normalize_first_level_keys=True, normalize_second_level_keys=True
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


def _compute_min_first_field_widths():
    """
    Compute the minimum first-field digit width per (species_prefix, gene_name)
    from allele_aliases canonical targets.

    For example, HLA-A canonical alleles have 2-digit first fields (A*01:01:01:01),
    while MICA uses 3-digit first fields (MICA*001:01:01).
    """
    from collections import Counter

    widths = {}
    for species_prefix, aliases in allele_aliases.items():
        if not hasattr(aliases, "items"):
            continue
        counters = {}
        for _alias_key, canonical in aliases.items():
            canonical = str(canonical)
            if "*" not in canonical or ":" not in canonical:
                continue
            gene_name, allele_part = canonical.split("*", 1)
            first_field = allele_part.split(":")[0]
            digits = first_field.lstrip("wW")
            if not digits.isdigit():
                continue
            key = (species_prefix, gene_name)
            if key not in counters:
                counters[key] = Counter()
            counters[key][len(digits)] += 1
        for key, counter in counters.items():
            # Use the most common width as the canonical minimum
            widths[key] = counter.most_common(1)[0][0]
    for species_prefix, genes in first_allele_field_widths.items():
        for gene_name, width in genes.items():
            widths[(species_prefix, str(gene_name))] = int(width)
    return widths


min_first_field_widths = _compute_min_first_field_widths()
