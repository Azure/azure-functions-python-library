# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
from typing import Optional, Any


class Datum:
    def __init__(self, value: Any, type: Optional[str]):
        self.value: Any = value
        self.type: Optional[str] = type

    @property
    def python_value(self) -> Any:
        if self.value is None or self.type is None:
            return None
        elif self.type in ('bytes', 'string', 'int', 'double'):
            return self.value
        elif self.type == 'json':
            return json.loads(self.value)
        elif self.type == 'collection_string':
            return [v for v in self.value.string]
        elif self.type == 'collection_bytes':
            return [v for v in self.value.bytes]
        elif self.type == 'collection_double':
            return [v for v in self.value.double]
        elif self.type == 'collection_sint64':
            return [v for v in self.value.sint64]
        else:
            return self.value

    @property
    def python_type(self) -> type:
        return type(self.python_value)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.value == other.value and self.type == other.type

    def __hash__(self):
        return hash((type(self), (self.value, self.type)))

    def __repr__(self):
        val_repr = repr(self.value)
        if len(val_repr) > 10:
            val_repr = val_repr[:10] + '...'
        return '<Datum {} {}>'.format(self.type, val_repr)
