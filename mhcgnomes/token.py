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
from .token_canonical_sequences import (
    CLASS1_TOKEN_SEQ,
    CLASS2_TOKEN_SEQ,
    ALPHA_CHAIN_TOKEN_SEQ,
    BETA_CHAIN_TOKEN_SEQ,
    MUTANT_TOKEN_SEQ
)

class Token(Serializable):
    def __init__(self, seq, raw_string=None):
        self.seq = seq
        if raw_string is None:
            raw_string = seq
        self.raw_string = raw_string

    def __str__(self):
        return "Token('%s')" % self.seq

    def __repr__(self):
        return "Token(seq='%s', raw_string='%s')" % (self.seq, self.raw_string)

    def __eq__(self, other):
        if type(other) is Token:
            return self.seq == other.seq
        elif type(other) is str:
            return self.seq == other
        else:
            return False

    def __hash__(self):
        return hash(self.seq)

    def __lt__(self, other):
        if type(other) is Token:
            return self.seq < other.seq
        elif type(other) is str:
            return self.seq < other
        else:
            return False

    @property
    def is_class1(self):
        return self.seq == CLASS1_TOKEN_SEQ

    @property
    def is_class2(self):
        return self.seq == CLASS2_TOKEN_SEQ

    @property
    def is_class1_or_class2(self):
        return self.is_class1 or self.is_class2

    @property
    def is_alpha(self):
        return self.seq == ALPHA_CHAIN_TOKEN_SEQ

    @property
    def is_beta(self):
        return self.seq == BETA_CHAIN_TOKEN_SEQ

    @property
    def is_alpha_or_beta(self):
        return self.is_alpha or self.is_beta

    @property
    def is_mutant(self):
        return self.seq == MUTANT_TOKEN_SEQ

    @property
    def is_slash(self):
        return self.seq == "/"

    @property
    def is_haplotype(self):
        return self.seq == "haplotype"

    @property
    def is_gene(self):
        return self.seq == "gene"

    @property
    def can_be_identifier(self):
        return not (
            self.is_alpha_or_beta or
            self.is_class1_or_class2 or
            self.is_slash or
            self.is_haplotype or
            self.is_gene
        )
