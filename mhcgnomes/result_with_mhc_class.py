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

from .mhc_class_helpers import is_class1, is_class2
from .result_with_species import ResultWithSpecies

class ResultWithMhcClass(ResultWithSpecies):
    """
    Common base class for any result object which has a species field.

    Useful for sharing helper methods that rely on the 'species' field.
    """
    def __init__(self, species, mhc_class, raw_string=None):
        ResultWithSpecies.__init__(self, species=species,raw_string=raw_string)
        self.mhc_class = mhc_class

    @property
    def has_mhc_class(self):
        return True

    @property
    def is_class1(self):
        return is_class1(self.mhc_class)

    @property
    def is_class2(self):
        return is_class2(self.mhc_class)
