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

from serializable import Serializable

import inspect

class Result(Serializable):
    """
    Base class for all parsed objects in mhcnames.
    """
    def __init__(self, raw_string=None):
        self.raw_string = raw_string

    @classmethod
    def init_field_names(cls):
        """
        Which fields are required to create a new instance of this object?

        By default extract everything except "self", "*args", and "**kwargs".
        """
        sig = inspect.signature(cls.__init__)
        params = sig.parameters
        init_arg_names = tuple([
            k for k, p in params.items()
            if k != "self" and p.kind not in {p.VAR_KEYWORD, p.VAR_POSITIONAL}
        ])
        return init_arg_names

    @classmethod
    def init_field_names_without_raw_string(cls):
        """
        Remove 'raw_string' from field names list to avoid
        e.g. having objects with identical

        """
        return tuple(
            [x for x in cls.init_field_names() if x != "raw_string"])


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
                results.append((k, "'%s'" % (v,)))
            else:
                results.append((k, "%s" % (v,)))
        return results
    
    def __str__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(
                ["%s=%s" % (k, v_str)
                for (k, v_str) in
                 self._field_name_string_pairs(self.str_field_names())
                ]))
                
    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(
                ["%s=%s" % (k, v_str)
                 for (k, v_str) in
                 self._field_name_string_pairs(self.repr_field_names())
                 ]))

    def to_string(self, include_species=True, use_old_species_prefix=False):
        raise NotImplementedError(
            "%s requires implementation of to_string() method" % (
                self.__class__.__name__))

    def compact_string(self, include_species=False, use_old_species_prefix=False):
        """
        Compact representation, defaults to omitting species
        """
        return self.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)


    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        for field in self.eq_field_names():
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    def __hash__(self):
        return sum(hash(getattr(self, field)) for field in self.hash_field_names())

    def to_record(self):
        raise NotImplementedError(
            "%s requires implementation of to_record() method" % (
                self.__class__.__name__))

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
        self_key = (self.__class__.__name__,) + self.to_tuple()
        other_key = (other.__class__.__name__,) + other.to_tuple()
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

    @property
    def has_gene(self):
        return False