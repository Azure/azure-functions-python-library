# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from enum import Enum
import os
import warnings

try:
    import orjson
    if 'AZUREFUNCTIONS_ORJSON' in os.environ:
        HAS_ORJSON = bool(os.environ['AZUREFUNCTIONS_ORJSON'])
    else:
        HAS_ORJSON = True
    import json
except ImportError:
    import json
    HAS_ORJSON = False


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


class StringifyEnumJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, StringifyEnum):
            return str(o)

        return super().default(o)


JSONDecodeError = json.JSONDecodeError

if HAS_ORJSON:
    def dumps(v, **kwargs):
        sort_keys = False
        if 'sort_keys' in kwargs:
            del kwargs['sort_keys']
            sort_keys = True
        if kwargs:  # Unsupported arguments
            return json.dumps(v, sort_keys=sort_keys, **kwargs)
        if sort_keys:
            r = orjson.dumps(v, option=orjson.OPT_SORT_KEYS)
        else:
            r = orjson.dumps(v)
        return r.decode(encoding='utf-8')

    def loads(*args, **kwargs):
        if kwargs:
            return json.loads(*args, **kwargs)
        else:  # ORjson takes no kwargs
            return orjson.loads(*args)

else:
    dumps = json.dumps
    loads = json.loads
