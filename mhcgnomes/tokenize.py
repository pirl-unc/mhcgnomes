
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

from .parsing_helpers import strip_chars

token_replacement_patterns = {
    # 'MHC' doesn't mean anything by itself since we're always
    # parsing MHC nomenclature here
    ("mhc",): None,

    # class I
    ("mhc-i",): "class-1",
    ("mhc-1",): "class-1",
    ("class-i",): "class-1",
    ("class", "1"): "class-1",
    ("class", "i"): "class-1",

    # class II
    ("mhc-ii",): "class-2",
    ("mhc-2",): "class-2",
    ("class-ii",): "class-2",
    ("class", "2"): "class-2",
    ("class", "ii"): "class-2",

    # Class II chains
    ("alpha", "chain"): "alpha",
    ("alpha-chain",): "alpha",
    ("beta", "chain"): "beta",
    ("beta-chain",): "beta",

    # 'mutant', 'mutation', 'mutations', are synonyms
    ("mutation",): "mutant",
    ("mutations",): "mutant",
}

replacement_pattern_lengths = {
    len(key)
    for key in token_replacement_patterns.keys()
}

# sorted in descending order
sorted_replacement_pattern_lengths = sorted(
    replacement_pattern_lengths, reverse=True)

def simplify_tokens(self, tokens, raw_string_parts):
    """
    Combine token pairs like ['alpha', 'chain'] into 'alpha-chain' and
    combine the corresponding raw string parts separated by a space.

    Also normalize token sequences like ['mhc' 'class' 'i'] into
    'class-1'.
    """
    result_tokens = []
    result_raw_string_parts = []
    n_tokens = len(tokens)

    for length in sorted_replacement_pattern_lengths:
        i = 0
        while i < n_tokens:
            key = tuple(tokens[i:i + length])
            if key in token_replacement_patterns:
                new_token = token_replacement_patterns[key]
                if new_token is not None:
                    result_tokens.append(new_token)
                    result_raw_string_parts.append(" ".join(
                        raw_string_parts[i:i + length]))
                i += length
            else:
                i += 1
    return result_tokens, result_raw_string_parts

def tokenize(name):
    """
    Returns two tuples:
        - canonical tokens
            e.g. ("class-2", "alpha")
        - original strings corresponding to each token
            e.g. ("MHC Class II", "alpha chain")
    """
    raw_string_parts = name.split()
    tokens = [
        strip_chars(p.lower(), "-, ").strip()
        for p in raw_string_parts
    ]
    return simplify_tokens(tokens, raw_string_parts)
