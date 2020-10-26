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

import yaml
from os.path import dirname, join

from .normalizing_dictionary import NormalizingDictionary

package_dir = dirname(__file__)
data_dir = join(package_dir, "data")


def get_path(yaml_filename):
    return join(data_dir, yaml_filename)

def load(
        yaml_filename,
        normalize_first_level_keys=False,
        normalize_second_level_keys=False):
    path = get_path(yaml_filename)
    with open(path, 'r') as f:
        result = yaml.safe_load(f)

    if normalize_second_level_keys:
        # turn first layer of values in dictionary into NormalizingDictionary
        result = {
            k: NormalizingDictionary.from_dict(v)
            for (k, v) in result.items()
        }

    if normalize_first_level_keys:
        result = NormalizingDictionary.from_dict(result)

    return result


# dictionary mapping scientific name -> info dictionary
species = load("species.yaml")

# Dictionary mapping each species prefix to a dictionary from old gene
# names to new ones
gene_aliases = load(
    "gene_aliases.yaml",
    normalize_first_level_keys=True,
    normalize_second_level_keys=True)

# Dictionary mapping each species prefix to a dictionary from
# old/retired/provisional allele names to standard new names
allele_aliases = load(
    "allele_aliases.yaml",
    normalize_first_level_keys=True,
    normalize_second_level_keys=True)

# Dictionary mapping species to haplotype name to list of alleles
haplotypes = load(
    "haplotypes.yaml",
    normalize_first_level_keys=True,
    normalize_second_level_keys=True)

# Dictionary mapping species to serotype name to list of alleles
serotypes = load(
    "serotypes.yaml",
    normalize_first_level_keys=True,
    normalize_second_level_keys=True)
