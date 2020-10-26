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

from __future__ import print_function, division, absolute_import

import pandas as pd

from .function_api import parse

def dataframe_from_parsed_objects(parsed_objects):
    records = [
        obj.to_record()
        for obj in parsed_objects
    ]
    return pd.DataFrame.from_records(records)


def dataframe_from_string_list(names):
    parsed_objects = [parse(name) for name in names]
    return dataframe_from_parsed_objects(parsed_objects)
