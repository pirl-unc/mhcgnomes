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

import pandas as pd

from . import function_api


def dataframe_from_parsed_objects(parsed_objects):
    """
    Create a pandas DataFrame from a list of parsed MHC objects.

    Each parsed object's `to_record()` method is called to generate a
    dictionary, which is then converted to a DataFrame row.

    Parameters
    ----------
    parsed_objects : list of Result
        List of parsed MHC objects (Allele, Gene, Species, etc.).

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns corresponding to the object fields.

    Examples
    --------
    >>> from mhcgnomes import parse
    >>> objects = [parse("HLA-A*02:01"), parse("HLA-B*07:02")]
    >>> df = dataframe_from_parsed_objects(objects)
    >>> df["gene"].tolist()
    ['HLA-A', 'HLA-B']
    """
    records = [
        obj.to_record()
        for obj in parsed_objects
    ]
    return pd.DataFrame.from_records(records)


def dataframe_from_string_list(names):
    """
    Parse a list of MHC allele strings and return a DataFrame.

    This is a convenience function that parses each string and creates
    a DataFrame from the results.

    Parameters
    ----------
    names : list of str
        List of MHC allele/gene/species strings to parse.

    Returns
    -------
    pandas.DataFrame
        DataFrame with parsed information for each input string.

    Examples
    --------
    >>> names = ["HLA-A*02:01", "HLA-B*07:02", "HLA-C*07:01"]
    >>> df = dataframe_from_string_list(names)
    >>> df["allele"].tolist()
    ['HLA-A*02:01', 'HLA-B*07:02', 'HLA-C*07:01']
    """
    parsed_objects = [function_api.parse(name) for name in names]
    return dataframe_from_parsed_objects(parsed_objects)
