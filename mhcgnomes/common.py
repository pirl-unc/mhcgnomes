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

from typing import Iterable

def unique(xs : Iterable):
    """
    Return iterable at most as long as the input, containing only its
    unique elements.
    """
    if type(xs) is list and len(xs) == 0 or len(xs) == 1:
        return xs
    return list(set(xs))

def arg_to_cache_key(x):
    if type(x) in {list, tuple}:
        value = tuple([arg_to_cache_key(xi) for xi in x])
    elif type(x) is dict:
        value = tuple([
            (arg_to_cache_key(k), arg_to_cache_key(v)) for (k, v) in x.items()])
    else:
        value = x
    return (type(x).__name__, value)

def cache(fn):
    """
    Memoization function which tries to freeze non-hashable types like
    dict and list, which depends on functions being called not modifying their
    arguments.
    """
    cache = {}
    def cached_fn(*args, **kwargs):
        args_key = arg_to_cache_key(args)
        kwargs_key = arg_to_cache_key(kwargs)
        key = (args_key, kwargs_key)
        if key not in cache:

            result = fn(*args, **kwargs)
            cache[key] = result
        return cache[key]
    return cached_fn

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
