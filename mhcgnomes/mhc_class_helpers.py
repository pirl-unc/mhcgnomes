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

class1_subtypes = {
    "Ia",
    "Ib",
    "Ic",
    "Id"
}

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
        (original_class is None and new_class is not None) or
        (original_class == "I" and new_class in class1_subtypes) or
        (original_class == "II" and new_class in class1_subtypes)
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


def restrict_alleles(alleles, mhc_class):
    if mhc_class == "I":
        valid_subtypes = class1_subtypes
    elif mhc_class == "II":
        valid_subtypes = class2_subtypes
    else:
        valid_subtypes = {mhc_class}

    return [
        allele
        for allele in alleles
        if allele.mhc_class in valid_subtypes
    ]


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
            raise ParseError("Invalid MHC class: '%s'" % original_string)
        else:
            return None
    return mhc_class
