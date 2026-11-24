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
from typing import Any

from .common import normalize_allele_alias
from .normalizing_dictionary import NormalizingDictionary
from .serotype_hierarchy import expand_serotype_memberships

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

    Runtime tables in this module (species, aliases, haplotypes, serotypes, ...)
    are loaded lazily on first attribute access and cached in module globals.

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
    import yaml

    path = get_path(yaml_filename)
    with open(path, encoding="utf-8") as f:
        result = yaml.safe_load(f)

    if normalize_second_level_keys:
        # turn first layer of values in dictionary into NormalizingDictionary
        result = {k: NormalizingDictionary.from_dict(v) for (k, v) in result.items()}

    if normalize_first_level_keys:
        result = NormalizingDictionary.from_dict(result)

    return result


def load_allele_aliases():
    """Load old/retired/provisional allele alias tables normalized per species."""
    return NormalizingDictionary.from_dict(
        {
            prefix: NormalizingDictionary.from_dict(aliases, normalize_fn=normalize_allele_alias)
            for prefix, aliases in load("allele_aliases.yaml").items()
        }
    )


def load_serotypes():
    """Expand curated direct serotype assignments with WMDA broad/split relationships."""
    direct = __getattr__("direct_serotypes")
    splits = __getattr__("serotype_splits")
    return NormalizingDictionary.from_dict(
        {
            prefix: NormalizingDictionary.from_dict(
                expand_serotype_memberships(assignments, splits.get(prefix, {}))
            )
            for prefix, assignments in direct.items()
        }
    )


def load_min_first_field_widths():
    """Build minimum first-field padding width map from first_allele_field_widths.yaml."""
    widths = __getattr__("first_allele_field_widths")
    return {
        (prefix, str(gene)): int(width)
        for prefix, genes in widths.items()
        for gene, width in genes.items()
    }


def load_current_allele_names():
    """Load sparse exact-current-name guards for alias lookup."""
    return {
        prefix: frozenset(normalize_allele_alias(name) for name in names)
        for prefix, names in load("current_allele_names.yaml").items()
    }


LAZY_DATA_LOADERS = {
    # dictionary mapping scientific name -> info dictionary
    "species": lambda: load("species.yaml"),
    # species -> [{alias, status, evidence}], attested prefix spellings imported
    # from the mhcseqs registry. See issue #136.
    "evidenced_prefix_aliases": lambda: load("evidenced_prefix_aliases.yaml"),
    # Curation holding area: source signal not yet stable enough for runtime (#136).
    "underrepresented_taxa_source_registry": lambda: load(
        "underrepresented_taxa_source_registry.yaml"
    ),
    # Dictionary mapping each species prefix to old gene names -> new gene names
    "gene_aliases": lambda: load(
        "gene_aliases.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Dictionary mapping each species prefix to old/retired allele names -> standard names
    "allele_aliases": load_allele_aliases,
    # Curated minimum width of the first allele field, keyed by species and gene
    "first_allele_field_widths": lambda: load("first_allele_field_widths.yaml"),
    # Dictionary mapping species -> gene -> list of known allele names
    "known_alleles": lambda: load(
        "known_alleles.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Dictionary mapping species to haplotype name to list of alleles
    "haplotypes": lambda: load(
        "haplotypes.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Curated direct serotype assignments (#196)
    "direct_serotypes": lambda: load(
        "serotypes.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Generated WMDA broad/split relationship graph
    "serotype_splits": lambda: load("serotype_splits.yaml", normalize_first_level_keys=True),
    # Expanded serotype memberships
    "serotypes": load_serotypes,
    # Dictionary mapping species to heterodimer shorthand to alpha/beta allele pairs
    "heterodimers": lambda: load(
        "heterodimers.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Dictionary mapping species to supertype name to supertype info
    "supertypes": lambda: load(
        "supertypes.yaml",
        normalize_first_level_keys=True,
        normalize_second_level_keys=True,
    ),
    # Complete allele names whose only field is numeric
    "single_field_alleles": lambda: load("single_field_alleles.yaml"),
    # Flattened (species_prefix, gene) -> minimum first field width map
    "min_first_field_widths": load_min_first_field_widths,
    # Sparse exact-current-name guards for alias lookup
    "current_allele_names": load_current_allele_names,
}


def __getattr__(name: str) -> Any:
    loader = LAZY_DATA_LOADERS.get(name)
    if loader is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = loader()
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(LAZY_DATA_LOADERS))
