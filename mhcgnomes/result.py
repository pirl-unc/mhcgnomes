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

import inspect
from dataclasses import dataclass
from typing import Union


@dataclass(eq=False, repr=False, frozen=True, init=False)
class Result:
    """
    Base class for all parsed objects in mhcgnomes.
    """

    raw_string: Union[str, None] = None

    def __init__(self, raw_string=None):
        object.__setattr__(self, "raw_string", raw_string)

    @staticmethod
    def _set_field(instance, field_name, field_value):
        object.__setattr__(instance, field_name, field_value)

    # Where the species on this result came from. Parser.parse records the
    # inputs; the value is worked out on first access and memoized here.
    # Neither is an __init__ field, so both stay out of equality, hashing,
    # repr and to_dict() -- two alleles that differ only in how their species
    # was determined are still the same allele.
    _species_source = None
    _species_source_inputs = None

    @property
    def species_source(self):
        """
        How this result's species was determined:

            "explicit"    the input named the species, e.g. "Gaga-BLB2*02"
            "inferred"  derived from a gene or allele name, e.g. "BLB2*02"
            "default"   fell back to default_species, e.g. "A*02:01"
            None        no species, or this object was built directly rather
                        than parsed

        Species inference is right most of the time and load-bearing when it is
        wrong, so a caller validating curated data can use this to reject any
        token whose species it did not actually supply.
        """
        if self._species_source is not None:
            return self._species_source
        if self._species_source_inputs is None:
            return None
        # Late import: species.py imports Result, so this cannot be top-level.
        from .species import Species, classify_species_source

        name, default_species = self._species_source_inputs
        species = self if type(self) is Species else getattr(self, "species", None)
        value = classify_species_source(name, species, default_species)
        Result._set_field(self, "_species_source", value)
        return value

    @property
    def species_inferred(self):
        """
        True when the species was not named in the input, i.e. species_source
        is "inferred" or "default". False when explicit, and False when there is
        no species to speak of.
        """
        return self.species_source in ("inferred", "default")

    @classmethod
    def init_field_names(cls):
        """
        Which fields are required to create a new instance of this object?

        By default extract everything except "self", "*args", and "**kwargs".
        """
        sig = inspect.signature(cls.__init__)
        params = sig.parameters
        init_arg_names = tuple(
            [
                k
                for k, p in params.items()
                if k != "self" and p.kind not in {p.VAR_KEYWORD, p.VAR_POSITIONAL}
            ]
        )
        return init_arg_names

    @classmethod
    def init_field_names_without_raw_string(cls):
        """
        Remove 'raw_string' from field names list to avoid
        e.g. having objects with identical

        """
        return tuple([x for x in cls.init_field_names() if x != "raw_string"])

    @classmethod
    def str_field_names(cls):
        """
        Which fields are includes in __str__ string.
        """
        return cls.init_field_names_without_raw_string()

    @classmethod
    def repr_field_names(cls):
        """
        Which fields are includes in __repr__ string.
        """
        return cls.str_field_names()

    @classmethod
    def tuple_field_names(cls):
        """
        Which fields are includes in the dict and tuple representations
        of this object.
        """
        return cls.init_field_names()

    @classmethod
    def eq_field_names(cls):
        """
        Which fields are includes in equality comparison.
        """
        return cls.init_field_names_without_raw_string()

    @classmethod
    def hash_field_names(cls):
        """
        Which fields are includes in the dict and tuple representations
        of this object.
        """
        return cls.eq_field_names()

    def _field_name_value_pairs(self, names):
        results = []
        for field_name in names:
            field_value = getattr(self, field_name)
            results.append((field_name, field_value))
        return results

    def _field_name_string_pairs(self, names):
        results = []
        for k, v in self._field_name_value_pairs(names):
            if isinstance(v, str):
                results.append((k, f"'{v}'"))
            else:
                results.append((k, f"{v}"))
        return results

    def __str__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                [
                    f"{k}={v_str}"
                    for (k, v_str) in self._field_name_string_pairs(self.str_field_names())
                ]
            ),
        )

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                [
                    f"{k}={v_str}"
                    for (k, v_str) in self._field_name_string_pairs(self.repr_field_names())
                ]
            ),
        )

    def to_string(self, include_species=True, use_old_species_prefix=False):
        raise NotImplementedError(
            f"{self.__class__.__name__} requires implementation of to_string() method"
        )

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        """
        Compact representation, defaults to omitting species
        """
        return self.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return all(getattr(self, field) == getattr(other, field) for field in self.eq_field_names())

    def __hash__(self):
        total = 0
        for field in self.hash_field_names():
            total += hash(getattr(self, field))
        return total

    def to_record(self):
        raise NotImplementedError(
            f"{self.__class__.__name__} requires implementation of to_record() method"
        )

    def to_tuple(self):
        keys = self.tuple_field_names()
        values = [getattr(self, k) for k in keys]
        return tuple(values)

    @classmethod
    def from_tuple(cls, t):
        keys = cls.tuple_field_names()
        assert len(keys) == len(t)
        d = dict(zip(keys, t))
        return cls.from_dict(d)

    def to_dict(self):
        return dict(zip(self.tuple_field_names(), self.to_tuple()))

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def copy(self, **kwargs):
        """
        Make a copy of this object and update any specified fields.
        """
        field_dict = self.to_dict()
        field_dict.update(kwargs)
        return self.__class__.from_dict(field_dict)

    def __lt__(self, other):
        self_key = (self.__class__.__name__, *self.to_tuple())
        other_key = (other.__class__.__name__, *other.to_tuple())
        return self_key < other_key

    ############################################################################
    #
    #  Default properties shared across all result objects
    #
    ############################################################################

    @property
    def annotation_null(self):
        return False

    @property
    def annotation_cystosolic(self):
        return False

    @property
    def annotation_secreted(self):
        return False

    @property
    def annotation_questionable(self):
        return False

    @property
    def annotation_low_expression(self):
        return False

    @property
    def annotation_aberrant_expression(self):
        return False

    @property
    def annotation_group(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False

    @property
    def annotation_pseudogene(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False

    @property
    def annotation_splice_variant(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return False

    @property
    def is_class1(self):
        return False

    @property
    def is_class2(self):
        return False

    @property
    def is_class2_alpha(self):
        return False

    @property
    def is_class2_beta(self):
        return False

    @property
    def has_species(self):
        return False

    @property
    def has_mhc_class(self):
        return False
