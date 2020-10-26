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

class NormalizingSet(object):
    """
    Like a regular set but all keys get normalized by a user
    provided function.
    """
    def __init__(
            self,
            *items,
            normalize_fn=normalize_string):
        self.item_to_original = {}
        self.items = set()
        self.normalize_fn = normalize_fn
        self.update(items)

    def copy(self):
        return NormalizingSet(*list(self), normalize_fn=self.normalize_fn)

    def __contains__(self, item):
        item = self.normalize_fn(item)
        return item in self.items

    def get_original(self, item):
        normalized = self.normalize_fn(item)
        return self.item_to_original.get(normalized)

    def add(self, extra_item):
        normalized = self.normalize_fn(extra_item)
        self.item_to_original[normalized] = extra_item
        self.items.add(normalized)

    def update(self, extra_items):
        for original in extra_items:
           self.add(original)

    def __iter__(self):
        for normalized in self.items:
            yield self.item_to_original[normalized]

    def __len__(self):
        return len(self.items)
