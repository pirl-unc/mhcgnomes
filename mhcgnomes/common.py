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

from functools import lru_cache


def cache(fn):
    """
    Memoization, should behave same as functools.cache from Python 3.9
    but will work with earlier 3.x Python versions.
    """
    return lru_cache(maxsize=None)(fn)


def normalize_string(name, chars_to_remove="-_'"):
    """
    Return uppercase string without any surrounding whitespace and
    without any characters such as '-', '_' or "'"
    """
    if type(name) in (float, int):
        name = str(name)

    if not isinstance(name, str):
        return name

    if " " in name:
        name = name.strip()
    name = name.upper()
    for char in chars_to_remove:
        if char in name:
            name = name.replace(char, "")
    return name


def normalize_dict_key(key):
    if type(key) in (list, tuple):
        return tuple([
            normalize_dict_key(sub_key)
            for sub_key in key
        ])
    else:
        return normalize_string(key)