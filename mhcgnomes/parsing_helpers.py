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


def strip_char(s : str, char_to_remove : str):
    while s.startswith(char_to_remove):
        s = s[1:]
    while s.endswith(char_to_remove):
        s = s[:-1]
    return s

def strip_chars(s : str, chars_to_remove):
    for c in chars_to_remove:
        s = strip_char(s, c)
    return s

def strip_whitespace_and_dashes(s : str):
    return strip_chars(s, "- ").strip()

def smart_split(seq : str, sep : str):
    """
    Split string on a separator and then get rid of dashes
    and empty strings
    """
    return [strip_whitespace_and_dashes(p) for p in seq.split(sep)]

def split_on_all_seps(seq : str, seps="_:"):
    """
    Split given string on all separators specified

    For example, 02_01:01 will be split_token_sequences into:
        ["02", "01", "01"]
    """
    string_parts = [seq]
    for sep in seps:
        new_parts = []
        for subseq in string_parts:
            new_parts.extend(smart_split(subseq, sep))
        parts = new_parts
    return parts


def split_digits_at_end(seq : str):
    """
    Splits strings like "A0201" into ("A", "0201")
    """
    prefix = seq
    suffix = ""
    while prefix and prefix[-1].isdigit():
        suffix = prefix[-1] + suffix
        prefix = prefix[:-1]
    return prefix, suffix


def contains_any_letters(s : str):
    """
    Returns True if any characters in the sequence are letters.
    """
    for si in s:
        if si.isalpha():
            return True
    return False

def contains_whitespace(s : str):
    """
    Returns True if any whitespace chars in input string.
    """
    return " " in s or "\t" in s

def split_allele_fields(
        str_after_gene,
        allow_three_digits_in_first_field,
        allow_three_digits_in_second_field):
    if ":" in str_after_gene:
        return str_after_gene.split(":")

    # if we don't have ':' to guide the field boundaries
    # then split_token_sequences on all possible seps and try to guess
    # which blocks of numbers are actually multiple fields.
    parts = split_on_all_seps(str_after_gene)

    parsed_fields = []
    failed = False
    for part in parts:
        if failed:
            break
        if part.isdigit():
            if (allow_three_digits_in_first_field and
                    len(parsed_fields) == 0 and
                    len(part) > 4):
                parsed_fields.append(part[:3])
                part = part[3:]
            if (allow_three_digits_in_second_field and
                    len(parsed_fields) == 1 and
                    len(part) > 4):
                parsed_fields.append(part[3:])

            while part and not failed:
                n_parsed = len(parsed_fields)
                remaining_length = len(part)
                if remaining_length == 1:
                    failed = True
                    break
                if (allow_three_digits_in_first_field and n_parsed == 0 and
                        (remaining_length == 3 or remaining_length > 4)):
                    boundary_index = 3
                elif (allow_three_digits_in_second_field and n_parsed == 1 and
                      (remaining_length == 3 or remaining_length > 4)):
                    boundary_index = 3
                else:
                    boundary_index = 2
                parsed_fields.append(part[:boundary_index])
                part = part[boundary_index:]
        else:
            parsed_fields.append(part)
    # if failed to parse anything then back up and try to turn some of
    # the optional arguments false
    if not failed and len(parsed_fields) > 0:
        return parsed_fields
    elif allow_three_digits_in_first_field:
        return split_allele_fields(
            str_after_gene,
            allow_three_digits_in_first_field=False,
            allow_three_digits_in_second_field=allow_three_digits_in_second_field)
    elif allow_three_digits_in_second_field:
        return split_allele_fields(
            str_after_gene,
            allow_three_digits_in_first_field=False,
            allow_three_digits_in_second_field=False)
    return None
