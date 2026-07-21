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

from .common import normalize_string


class NormalizingSet:
    """
    Like a regular set but all keys get normalized by a user
    provided function.
    """

    def __init__(self, *items, normalize_fn=normalize_string):
        self.item_to_original = {}
        self.items = set()
        self.normalize_fn = normalize_fn
        self._frozen = False
        self.update(items)

    def copy(self):
        return NormalizingSet(*list(self), normalize_fn=self.normalize_fn)

    def freeze(self):
        self._frozen = True
        return self

    @property
    def is_frozen(self):
        return self._frozen

    def _check_mutable(self):
        if self._frozen:
            raise TypeError("NormalizingSet is frozen")

    def __contains__(self, item):
        normalized = self.normalize_fn(item)
        if normalized is None:
            return False
        return normalized in self.items

    def __eq__(self, other):
        if type(other) is not NormalizingSet:
            return False
        if len(self) != len(other):
            return False
        return self.items == other.items

    def get_original(self, item):
        normalized = self.normalize_fn(item)
        if normalized is None:
            return None
        return self.item_to_original.get(normalized)

    def add(self, extra_item):
        self._check_mutable()
        normalized = self.normalize_fn(extra_item)
        if normalized is not None:
            self.item_to_original[normalized] = extra_item
            self.items.add(normalized)

    def update(self, extra_items):
        self._check_mutable()
        for original in extra_items:
            self.add(original)

    def __iter__(self):
        for normalized in self.items:
            yield self.item_to_original[normalized]

    def __len__(self):
        return len(self.items)
