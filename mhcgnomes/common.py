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
    result = []
    unique_set = set()
    for xi in xs:
        if xi in unique_set:
            continue
        result.append(xi)
        unique_set.add(xi)
    return result

def arg_to_cache_key(x, _primitive_types={bool, int, str, float}):
    if x is None:
        return None

    t = type(x)
    if t is int or t is str or t is bool or t is float:
        return x

    if t in {list, tuple}:
        if len(x) == 0:
            value = ()
        elif len(x) == 1:
            value = (arg_to_cache_key(x[0]),)
        else:
            value = tuple([arg_to_cache_key(xi) for xi in x])
    elif t is dict:
        value = tuple([
            (arg_to_cache_key(k), arg_to_cache_key(v)) for (k, v) in x.items()])
    else:
        value = x
    return (t.__name__, value)

def cache(fn):
    """
    Memoization function which tries to freeze non-hashable types like
    dict and list, which depends on functions being called not modifying their
    arguments.
    """
    cache = {}
    def cached_fn(*args, **kwargs):
        if not args:
            args_key = ()
        else:
            args_key = arg_to_cache_key(args)
        if not kwargs:
            kwargs_key = ()
        else:
            kwargs_key = arg_to_cache_key(kwargs)
        key = (args_key, kwargs_key)
        if key not in cache:
            result = fn(*args, **kwargs)
            cache[key] = result
        return cache[key]
    return cached_fn


def normalize_string(name, _cache={}, _chars_to_remove="-_':"):
    """
    Return uppercase string without any surrounding whitespace and
    without any characters such as '-', '_' ':' or "'"
    """
    if name in _cache:
        return _cache[name]

    if name is None:
        result = None
    else:
        t = type(name)
        if t is float or t is int:
            result = str(name)
        elif t is not str:
            result = name
        else:
            name = name.strip().upper()
            for char in _chars_to_remove:
                if char in name:
                    name = name.replace(char, "")
            result = name
    _cache[name] = result
    return result


def normalize_dict_key(key):
    if type(key) in (list, tuple):
        return tuple([
            normalize_dict_key(sub_key)
            for sub_key in key
        ])
    else:
        return normalize_string(key)
