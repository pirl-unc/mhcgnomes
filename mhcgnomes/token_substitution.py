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

from .token_canonical_sequences import (
    CLASS1_TOKEN_SEQ,
    CLASS2_TOKEN_SEQ,
    ALPHA_CHAIN_TOKEN_SEQ,
    BETA_CHAIN_TOKEN_SEQ,
    MUTANT_TOKEN_SEQ
)
from .token import Token

token_replacement_patterns = {
    # 'MHC' doesn't mean anything by itself since we're always
    # parsing MHC nomenclature here
    ("major", "histocompatibility", "complex"): None,
    ("mhc",): None,
    ("major", "histocompatibility", "antigen",): None,
    ("histocompatibility", "antigen",): None,
    ("leukocyte", "antigen",): None,
    # a lot of the HLA sequence s
    ("fragment",): None,
    ("exons", "1-3"): None,
    ("exons", "1-2"): None,

    # class I
    ("mhc-i",): CLASS1_TOKEN_SEQ,
    ("mhc-1",): CLASS1_TOKEN_SEQ,
    ("class-i",): CLASS1_TOKEN_SEQ,
    ("class", "1"): CLASS1_TOKEN_SEQ,
    ("class", "i"): CLASS1_TOKEN_SEQ,

    # class II
    ("mhc-ii",): CLASS2_TOKEN_SEQ,
    ("mhc-2",): CLASS2_TOKEN_SEQ,
    ("class-ii",): CLASS2_TOKEN_SEQ,
    ("class", "2"): CLASS2_TOKEN_SEQ,
    ("class", "ii"): CLASS2_TOKEN_SEQ,

    # Class II chains
    ("alpha", "chain"): ALPHA_CHAIN_TOKEN_SEQ,
    ("alpha-chain",): ALPHA_CHAIN_TOKEN_SEQ,
    ("beta", "chain"): BETA_CHAIN_TOKEN_SEQ,
    ("beta-chain",): BETA_CHAIN_TOKEN_SEQ,

    # 'mutant', 'mutation', 'mutations', are synonyms
    ("mutation",): MUTANT_TOKEN_SEQ,
    ("mutations",): MUTANT_TOKEN_SEQ,
}

replacement_pattern_lengths = {
    len(key)
    for key in token_replacement_patterns.keys()
}

# sorted in descending order
sorted_replacement_pattern_lengths = sorted(
    replacement_pattern_lengths, reverse=True)

def apply_token_substitutions(tokens, length):
    """
    Replace all subsequences of `length` token_strings with any replacements
    found in the dictionary above.
    """
    result_tokens = []
    ignored_tokens = []
    i = 0
    n_tokens = len(tokens)
    while i < n_tokens:
        found_in_dict = False
        if i < n_tokens - length + 1:
            key = tuple([tokens[j].seq for j in range(i, i + length)])
            if key in token_replacement_patterns:
                found_in_dict = True
                new_token_seq = token_replacement_patterns[key]
                if new_token_seq is None:
                    ignored_tokens.extend(key)
                else:
                    new_token = Token(
                        seq=new_token_seq,
                        raw_string=" ".join(
                            [tokens[j].raw_string for j in range(i, i + length)]))
                    result_tokens.append(new_token)

        if found_in_dict:
            i += length
        else:
            result_tokens.append(tokens[i])
            i += 1
    return (
        result_tokens,
        ignored_tokens,
    )

def simplify_tokens(tokens):
    """
    Combine token pairs like ['alpha', 'chain'] into 'alpha-chain' and
    combine the corresponding raw string parts separated by a space.

    Also normalize token sequences like ['mhc' 'class' 'i'] into canonical
    tokens like 'class-1'.
    """
    ignored_tokens = []
    for length in sorted_replacement_pattern_lengths:
        tokens, curr_ignored_tokens = apply_token_substitutions(tokens, length)
        ignored_tokens.extend(curr_ignored_tokens)
    return tokens, ignored_tokens
