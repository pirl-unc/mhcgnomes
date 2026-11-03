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

from collections.abc import Iterable
from functools import wraps


def unique(xs: Iterable):
    """
    Return iterable at most as long as the input, containing only its
    unique elements.
    """
    if type(xs) is list and (len(xs) == 0 or len(xs) == 1):
        return xs
    result = []
    unique_set = set()
    for xi in xs:
        if xi in unique_set:
            continue
        result.append(xi)
        unique_set.add(xi)
    return result


def arg_to_cache_key(x):
    if x is None:
        return None

    t = type(x)

    if t is int or t is str or t is bool or t is float or t is type:
        return x

    if t is list or t is tuple:
        if len(x) == 0:
            return ()
        elif len(x) == 1:
            return (arg_to_cache_key(x[0]),)
        else:
            value = tuple([arg_to_cache_key(xi) for xi in x])
    elif t is dict:
        if len(x) == 0:
            value = ()
        elif len(x) == 1:
            ((k, v),) = x.items()
            value = (arg_to_cache_key(k), arg_to_cache_key(v))
        else:
            value = tuple([(arg_to_cache_key(k), arg_to_cache_key(v)) for (k, v) in x.items()])
    else:
        value = x
    return (t.__name__, value)


def cache(fn):
    """
    Memoization function which tries to freeze non-hashable types like
    dict and list, which depends on functions being called not modifying their
    arguments.
    """
    cache_dict = {}

    @wraps(fn)
    def cached_fn(*args, **kwargs):
        args_key = arg_to_cache_key(args)
        if not kwargs:
            kwargs_key = ()
        else:
            kwargs_key = arg_to_cache_key(kwargs)
        key = (args_key, kwargs_key)
        if key not in cache_dict:
            result = fn(*args, **kwargs)
            cache_dict[key] = result
        return cache_dict[key]

    return cached_fn


def normalize_string(name):
    """
    Normalize a name into the key used for case- and punctuation-blind lookup.

    This is the default key function of NormalizingDictionary and
    NormalizingSet, so every species, gene, allele and alias table is keyed
    by it.

    Parameters
    ----------
    name : str, int, float, None, or other
        Name to normalize.

    Returns
    -------
    str, None, or other
        For a str: the name with every '-', '_', "'" and ':' removed,
        surrounding whitespace stripped, and upper-cased. For an int or
        float: str(name). For None: None. Any other value is returned
        unchanged.
    """
    if name is None:
        return None

    t = type(name)
    if t is float or t is int:
        return str(name)
    if t is not str:
        return name
    return name.replace("-", "").replace("_", "").replace("'", "").replace(":", "").strip().upper()
