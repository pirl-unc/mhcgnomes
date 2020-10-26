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

import re

from typing import Union

from .errors import ParseError
from .result import Result

class Mutation(Result):

    def __init__(
            self,
            pos : int,
            aa_original : str,
            aa_mutant : str,
            raw_string : Union[str, None] = None):
        Result.__init__(self, raw_string=raw_string)
        self.pos = pos
        self.aa_original = aa_original
        self.aa_mutant = aa_mutant

    def fields(self):
        return ("pos", "aa_original", "aa_mutant")

    def to_string(self):
        return "%s%d%s" % (self.aa_original, self.pos, self.aa_mutant)

    mutation_regex = re.compile("([a-yA-Y])(\d+)([a-yA-Y])")

    @classmethod
    def get(cls, pos, aa_original, aa_mutant, raw_string=None):
        pos = int(pos)
        aa_original = aa_original.upper()
        aa_mutant = aa_mutant.upper()
        return Mutation(pos, aa_original, aa_mutant)

    @classmethod
    def parse(cls, seq, raise_on_error=True):
        seq = seq.upper()
        result = cls.mutation_regex.fullmatch(seq)
        if result is None:
            if raise_on_error:
                raise ParseError("Allele mutation malformed: '%s'" % seq)
            else:
                return None
        return cls.get(
            pos=result.group(2),
            aa_original=result.group(1),
            aa_mutant=result.group(3),
            raw_string=seq)
