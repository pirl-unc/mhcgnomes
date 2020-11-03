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

from .common import cache
from .parsing_helpers import strip_chars
from .token import Token
from .token_substitution import simplify_tokens

class TokenizationResult(Serializable):
    def __init__(
            self,
            tokens,
            ignored_tokens,
            attributes,
            raw_string,
            trimmed_string):
        self.tokens = tuple(tokens)
        self.ignored_tokens = tuple(ignored_tokens)
        self.attributes = attributes
        self.raw_string = raw_string
        self.trimmed_string = trimmed_string


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

def split_token_sequences(s, token_seps="/"):
    """
    Split string on whitespace. Also split_token_sequences on slashes but preserve
    them in the token sequence.
    """
    results = s.split()
    for sep in token_seps:
        new_results = []
        for part in results:
            for i, sub_part in enumerate(part.split(sep)):
                if i > 0:
                    new_results.append(sep)
                new_results.append(sub_part)
        results = new_results
    return results

def split_and_extract_attributes(s):
    parts = split_token_sequences(s)
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

def strip_whitespace_and_remove_quotes(name : str):
    return name.replace("\"", "").replace("'", "").strip()

@cache
def tokenize(name):
    """
    Splits name into token sequence and returns TokenizationResult which
    contains a sequence of Token objects.
    """
    trimmed_name = strip_whitespace_and_remove_quotes(name)
    raw_string_parts, attributes = split_and_extract_attributes(trimmed_name)
    token_sequences = [normalize_token(p) for p in raw_string_parts]
    tokens = [
        Token(seq, raw_string)
        for (seq, raw_string) in zip(token_sequences, raw_string_parts)]
    tokens, ignored_tokens =  simplify_tokens(tokens)
    return TokenizationResult(
        tokens=tokens,
        ignored_tokens=ignored_tokens,
        attributes=attributes,
        raw_string=name,
        trimmed_string=trimmed_name)
