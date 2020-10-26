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

from collections import defaultdict

from .common import normalize_string

class NormalizingDictionary(object):
    """
    Like a regular dictionary but all keys get normalized by a user
    provided function.

    Caution: the number of items in keys() and values() for this dictionary
    may differ because two distinct keys may be transformed to the same
    underlying normalized key and thus will share a value.
    """
    def __init__(
            self,
            *pairs,
            normalize_fn=normalize_string,
            default_value_fn=None):
        self.store = {}
        self.original_to_normalized_key_dict = {}
        self.normalized_to_original_keys_dict = defaultdict(set)
        self.normalize_fn = normalize_fn
        self.default_value_fn = default_value_fn
        self.update_pairs(pairs)

    def copy(self):
        keys = list(self.keys())
        values = [self.__getitem__(k) for k in keys]
        pairs = zip(keys, values)
        return NormalizingDictionary(
            *pairs,
            normalize_fn=self.normalize_fn,
            default_value_fn=self.default_value_fn)

    def update_pairs(self, pairs):
        # populate dictionary with initial values via calls to __setitem__
        for (k, v) in pairs:
            self.__setitem__(k, v)

    def update(self, other_dict):
        self.update_pairs(other_dict.items())

    def __getitem__(self, k):
        k_normalized = self.normalize_fn(k)
        if k_normalized not in self.store:
            if self.default_value_fn is not None:
                self.store[k_normalized] = self.default_value_fn()
            else:
                raise KeyError(k)
        return self.store[k_normalized]

    def __setitem__(self, k, v):
        if k is None:
            raise ValueError("Key cannot be None in __setitem__")
        k_normalized = self.normalize_fn(k)
        self.original_to_normalized_key_dict[k] = k_normalized
        self.normalized_to_original_keys_dict[k_normalized].add(k)
        self.store[k_normalized] = v

    def __contains__(self, k):
        k_normalized = self.normalize_fn(k)
        return k_normalized in self.store

    def original_keys(self, k):
        """
        Returns set of original keys which match the normalized representation
        of the given key.
        """
        k_normalized = self.normalize_fn(k)
        original_keys = self.normalized_to_original_keys_dict.get(k_normalized)
        if original_keys is None:
            return set()
        return original_keys

    def original_key(self, k, default_value=None, pick_best_fn=None):
        """
        Attempts to get a single original key matching which has
        the same the normalized representation as the given input,
        but may raise an exception if there are more than one original
        key that matches.
        """
        ks = list(self.original_keys(k))

        if len(ks) == 0:
            if default_value is None:
                raise KeyError(k)
            else:
                return default_value
        elif len(ks) > 1:
            if pick_best_fn is None:
                raise ValueError(
                    "Key '%s' matches multiple entries: %s" % (
                        k, ks,))
            else:
                return pick_best_fn(ks)
        else:
            return ks[0]

    def get(self, k, v=None):
        return self.store.get(self.normalize_fn(k), v)

    def keys(self):
        return self.original_to_normalized_key_dict.keys()

    def normalized_keys(self):
        return self.store.keys()

    def key_sets_aligned_with_values(self):
        """
        Returns all of the original keys associated with each item
        of values
        """
        results = []
        for normalized_key in self.normalized_keys():
            original_keys = self.normalized_to_original_keys_dict[normalized_key]
            if not normalized_key or not original_keys:
                raise ValueError("Bad key pair (%s, %s)" % (
                    normalized_key, original_keys))
            results.append((normalized_key, original_keys))
        return results

    def keys_aligned_with_values(self):
        """
        Returns one of the original keys associated with each item
        of values
        """
        for (normalized_key, original_keys) in self.key_sets_aligned_with_values():
            if len(original_keys) == 0:
                raise ValueError("Key set unexpectedly empty")
            yield sorted(original_keys)[0]

    def values(self):
        return self.store.values()

    def __iter__(self):
        for k in self.keys_aligned_with_values():
            yield k

    def items(self):
        return zip(
            self.keys_aligned_with_values(),
            self.values())

    def to_dict(self):
        return {
            k: v
            for (k,v) in self.items()
        }

    def map_values(self, fn):
        pairs = []
        for k, v in self.items():
            if not k:
                raise ValueError("Empty key")
            if v is None:
                raise ValueError("Empty value for '%s'" % k)
            v2 = fn(v)
            pairs.append((k, v2))

        return NormalizingDictionary(
            *pairs,
            normalize_fn=self.normalize_fn,
            default_value_fn=self.default_value_fn)

    def map_keys(self, fn):
        pairs = [
            (fn(k), v)
            for (k, v) in self.items()
        ]
        return NormalizingDictionary(
            *pairs,
            normalize_fn=self.normalize_fn,
            default_value_fn=self.default_value_fn)

    def invert(self):
        """
        Returns a NormalizingDictionary where every value
        is associated with a set of keys which mapped to it. When
        values are collections (list, set, or tuple) then the elements
        of the collection are turned into individual keys.
        """
        result = NormalizingDictionary(
            normalize_fn=self.normalize_fn,
            default_value_fn=set)

        for (k, v) in self.items():
            if isinstance(v, (list, tuple, set)):
                values = v
            else:
                values = [v]

            for vi in values:
                result[vi].add(k)
        return result

    def __len__(self):
        return len(self.store)

    @classmethod
    def from_dict(cls, d, normalize_fn=normalize_string, default_value_fn=None):
        if type(d) is NormalizingDictionary:
            return d.copy()
        result = cls(
            *d.items(),
            normalize_fn=normalize_fn,
            default_value_fn=default_value_fn)
        if len(d) != 0:
            assert len(result) > 0
            assert len(result.store) > 0
            assert len(result.original_to_normalized_key_dict) > 0
            assert len(result.normalized_to_original_keys_dict) > 0
        return result

    def __str__(self):
        s = (
            "<NormalizingDictionary with %d unique items, "
            "normalize_fn=%s, "
            "default_value_fn=%s>") % (
                len(self.store),
                self.normalize_fn,
                self.default_value_fn)
        all_items = list(self.items())

        for i, (k, v) in enumerate(all_items):
            s += "\n\t%s: %s" % (k, v)
            if i > 10:
                s += "\n..."
                break
        return s

    def __repr__(self):
        return str(self)
