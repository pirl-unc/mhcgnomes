
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

CLASS1_TOKEN = "class-1"
CLASS2_TOKEN = "class-2"
ALPHA_CHAIN_TOKEN = "alpha"
BETA_CHAIN_TOKEN = "beta"
MUTANT_TOKEN = "mutant"

token_replacement_patterns = {
    # 'MHC' doesn't mean anything by itself since we're always
    # parsing MHC nomenclature here
    ("mhc",): None,
    ("major", "histocompatibility", "antigen",): None,
    ("histocompatibility", "antigen",): None,
    # a lot of the HLA sequence s
    ("fragment",): None,
    ("exons", "1-3"): None,
    ("exons", "1-2"): None,

    # class I
    ("mhc-i",): CLASS1_TOKEN,
    ("mhc-1",): CLASS1_TOKEN,
    ("class-i",): CLASS1_TOKEN,
    ("class", "1"): CLASS1_TOKEN,
    ("class", "i"): CLASS1_TOKEN,

    # class II
    ("mhc-ii",): CLASS2_TOKEN,
    ("mhc-2",): CLASS2_TOKEN,
    ("class-ii",): CLASS2_TOKEN,
    ("class", "2"): CLASS2_TOKEN,
    ("class", "ii"): CLASS2_TOKEN,

    # Class II chains
    ("alpha", "chain"): ALPHA_CHAIN_TOKEN,
    ("alpha-chain",): ALPHA_CHAIN_TOKEN,
    ("beta", "chain"): BETA_CHAIN_TOKEN,
    ("beta-chain",): BETA_CHAIN_TOKEN,

    # 'mutant', 'mutation', 'mutations', are synonyms
    ("mutation",): MUTANT_TOKEN,
    ("mutations",): MUTANT_TOKEN,
}

replacement_pattern_lengths = {
    len(key)
    for key in token_replacement_patterns.keys()
}

# sorted in descending order
sorted_replacement_pattern_lengths = sorted(
    replacement_pattern_lengths, reverse=True)

def apply_replacements(tokens, raw_string_parts, length):
    """
    Replace all subsequences of `length` tokens with any replacements
    found in the dictionary above.
    """
    result_tokens = []
    result_raw_string_parts = []
    i = 0
    n_tokens = len(tokens)
    while i < n_tokens:
        key = tuple(tokens[i:i + length])
        if key in token_replacement_patterns:
            new_token = token_replacement_patterns[key]
            if new_token is not None:
                result_tokens.append(new_token)
                new_raw_string_part = " ".join(
                    raw_string_parts[i: i + length])
                result_raw_string_parts.append(new_raw_string_part)
            i += length
        else:
            result_tokens.append(tokens[i])
            result_raw_string_parts.append(raw_string_parts[i])
            i += 1
    return result_tokens, result_raw_string_parts

def simplify_tokens(tokens, raw_string_parts):
    """
    Combine token pairs like ['alpha', 'chain'] into 'alpha-chain' and
    combine the corresponding raw string parts separated by a space.

    Also normalize token sequences like ['mhc' 'class' 'i'] into
    'class-1'.
    """
    for length in sorted_replacement_pattern_lengths:
        tokens, raw_string_parts = apply_replacements(tokens, raw_string_parts, length)
    return tokens, raw_string_parts

def deparen(s):
    """
    Remove all interior parantheses from sequence.
    """
    return s.replace("(", "").replace(")", "")

def normalize_token(s):
    """
    Apply all string transformations to turn non-whitespace character sequence
    into a token.
    """
    return strip_chars(deparen(s.lower()), "-, ").strip()

def split_and_extract_attributes(s):
    parts = s.split()
    if "=" not in s:
        return parts, {}

    parts_before_attributes = []
    attributes = {}
    found_first_attribute = False
    attribute_key_in_progress = None
    attribute_values_in_progress = None
    for part in parts:
        if part.count("=") == 1:
            found_first_attribute = True
            if attribute_key_in_progress:
                attributes[attribute_key_in_progress] = " ".join(attribute_values_in_progress)
            attribute_key_in_progress, first_value = part.split("=")
            attribute_values_in_progress = [first_value]
        elif not found_first_attribute:
            parts_before_attributes.append(part)
        else:
            attribute_values_in_progress.append(part)
    if attribute_key_in_progress:
        attributes[attribute_key_in_progress] = " ".join(attribute_values_in_progress)
    return parts_before_attributes, attributes

def tokenize(name):
    """
    Returns two tuples and a dictionary:
        - canonical tokens
            e.g. (CLASS2_TOKEN, "alpha")
        - original strings corresponding to each token
            e.g. ("MHC Class II", "alpha chain")
    """
    raw_string_parts, attributes = split_and_extract_attributes(name)
    tokens = [normalize_token(p) for p in raw_string_parts]
    tokens, raw_string_parts =  simplify_tokens(tokens, raw_string_parts)
    return tuple(tokens), tuple(raw_string_parts), attributes