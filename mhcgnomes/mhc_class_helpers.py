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

from .errors import ParseError

class1_subtypes = {"Ia", "Ib", "Ic", "Id"}

class2_subtypes = {
    "IIa",
    "IIb",
}

class1_restrictions = {"I"}.union(class1_subtypes)
class2_restrictions = {"II"}.union(class2_subtypes)

valid_class_restrictions = class1_restrictions.union(class2_restrictions)

classical_subtypes = {"Ia", "IIa"}


def mhc_class_is_more_specific(original_class=None, new_class=None):
    return (
        (original_class is None and new_class is not None)
        or (original_class == "I" and new_class in class1_subtypes)
        or (original_class == "II" and new_class in class2_subtypes)
    )


def is_class1(mhc_class):
    return mhc_class in class1_restrictions


def is_class2(mhc_class):
    return mhc_class in class2_restrictions


def is_valid_restriction(original_class=None, new_class=None):
    if original_class is None:
        return True

    if new_class is None:
        # once we've restricted, can't go backwards
        return False

    if original_class == new_class:
        return True

    return mhc_class_is_more_specific(original_class, new_class)


def mhc_classes_within(mhc_class):
    """
    The MHC class strings that satisfy a restriction to ``mhc_class``.

    Shared by restrict_alleles and restrict_genes so that alleles and genes
    are filtered by the same table.

    Parameters
    ----------
    mhc_class : str
        Class restriction, e.g. "I", "II", "Ia" or "IIb".

    Returns
    -------
    frozenset of str
        The contents of class1_restrictions for "I" ("I" plus its subtypes
        "Ia" to "Id"), of class2_restrictions for "II" ("II", "IIa", "IIb"),
        and otherwise just ``mhc_class`` itself.
    """
    if mhc_class == "I":
        return frozenset(class1_restrictions)
    if mhc_class == "II":
        return frozenset(class2_restrictions)
    return frozenset({mhc_class})


def restrict_alleles(alleles, mhc_class):
    valid_subtypes = mhc_classes_within(mhc_class)
    return [allele for allele in alleles if allele.mhc_class in valid_subtypes]


def restrict_genes(genes, mhc_class):
    """
    The gene-level twin of restrict_alleles, sharing its subtype table.

    Written because Haplotype.absent_genes has to survive a class restriction
    on the same terms as the alleles beside it. is_valid_restriction answers a
    different question -- may this restriction be applied at all -- and returns
    False for ("Ia", "I"), so using it here silently dropped a class I locus
    from a class I reading.
    """
    valid_subtypes = mhc_classes_within(mhc_class)
    return [gene for gene in genes if gene.mhc_class in valid_subtypes]


def normalize_mhc_class_string(mhc_class, raise_on_error=True):
    original_string = mhc_class
    mhc_class = mhc_class.lower()
    if mhc_class.startswith("class-"):
        _, mhc_class = mhc_class.split("class-")
    elif mhc_class.startswith("class "):
        _, mhc_class = mhc_class.split("class ")
    mhc_class = mhc_class.replace("i", "I")
    mhc_class = mhc_class.replace("1", "I")
    mhc_class = mhc_class.replace("2", "II")
    if mhc_class not in valid_class_restrictions:
        if raise_on_error:
            raise ParseError(f"Invalid MHC class: '{original_string}'")
        else:
            return None
    return mhc_class
