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


from .result import Result

class ResultWithSpecies(Result):
    """
    Common base class for any result object which has a species field.

    Useful for sharing helper methods that rely on the 'species' field.
    """
    def __init__(self, species, raw_string=None):
        Result.__init__(self, raw_string=raw_string)
        self.species = species

    @property
    def has_species(self):
        return True

    @property
    def species_prefix(self):
        return self.species.prefix

    @property
    def species_common_name(self):
        return self.species.common_species_name

    @property
    def common_species_name(self):
        return self.species.common_species_name

    @property
    def is_mouse(self):
        return self.species.is_mouse

    @property
    def is_chicken(self):
        return self.species.is_chicken

    @property
    def is_rat(self):
        return self.species.is_rat

    @property
    def is_human(self):
        return self.species.is_human

    @property
    def is_dog(self):
        return self.species.is_dog

    @property
    def is_cat(self):
        return self.species.is_cat

    @property
    def is_pig(self):
        return self.species.is_pig

    @property
    def is_cow(self):
        return self.species.is_cow

    @property
    def is_horse(self):
        return self.species.is_horse

