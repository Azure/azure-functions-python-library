# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from enum import Enum
import os

AZUREFUNCTIONS_UJSON_ENV_VAR = 'AZUREFUNCTIONS_UJSON'

try:
    import ujson
    if AZUREFUNCTIONS_UJSON_ENV_VAR in os.environ:
        HAS_UJSON = bool(os.environ[AZUREFUNCTIONS_UJSON_ENV_VAR])
    else:
        HAS_UJSON = True
    import json
except ImportError:
    import json
    HAS_UJSON = False


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)

    def __json__(self):
        """For ujson encoding."""
        return f'"{self.name}"'


class StringifyEnumJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, StringifyEnum):
            return str(o)

        return super().default(o)


JSONDecodeError = json.JSONDecodeError

if HAS_UJSON:
    def dumps(v, **kwargs):
        if 'default' in kwargs:
            return json.dumps(v, **kwargs)

        if 'cls' in kwargs:
            del kwargs['cls']
        
        return ujson.dumps(v, **kwargs)

    def loads(*args, **kwargs):
        if kwargs:
            return json.loads(*args, **kwargs)
        else:  # ujson takes no kwargs
            return ujson.loads(*args)

else:
    dumps = json.dumps
    loads = json.loads
