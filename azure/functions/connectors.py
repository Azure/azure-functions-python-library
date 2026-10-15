# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import typing

from . import meta


class ConnectorTriggerConverter(meta.InConverter, binding='connectorTrigger',
                                trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        valid_types = (str, dict, bytes)
        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata):
        """
        Decode incoming connector trigger request data.
        Returns scalar data unchanged or collection data as a list.
        """
        # Only explicit collection types identify batches; JSON arrays can be single events.
        if data.type in ('collection_string', 'collection_bytes'):
            return cls.decode_multiple_messages(data, trigger_metadata=trigger_metadata)
        return cls.decode_single_message(data, trigger_metadata=trigger_metadata)

    @classmethod
    def decode_single_message(cls, data: meta.Datum, *, trigger_metadata):
        """Decode a single connector event, preserving the existing scalar format."""
        # Handle different data types appropriately
        if data.type == 'json':
            # If it's already parsed JSON, use the value directly
            return data.value
        elif data.type == 'string':
            # If it's a string, use it as-is
            return data.value
        elif data.type == 'bytes':
            return data.value
        else:
            # Fallback to python_value for other types
            return data.python_value if hasattr(data, 'python_value') else data.value

    @classmethod
    def decode_multiple_messages(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> typing.List[typing.Union[str, dict, bytes]]:
        """Decode cardinality many payloads without parsing individual event strings."""
        if data.type == 'collection_string':
            return list(data.value.string)
        elif data.type == 'collection_bytes':
            return list(data.value.bytes)
        elif data.type == 'json':
            parsed_data = json.loads(data.value) if isinstance(data.value, str) else data.value
            if isinstance(parsed_data, list):
                return parsed_data
            raise ValueError('expected a JSON array for multiple connector messages')
        else:
            raise NotImplementedError('unable to decode multiple messages '
                                      f'with data type {data.type}')

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type] = None):
        """
        Encode the return value from connector trigger functions.
        """
        if obj is None:
            return meta.Datum(type='string', value='')
        elif isinstance(obj, str):
            return meta.Datum(type='string', value=obj)
        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        elif isinstance(obj, dict):
            return meta.Datum(type='string', value=json.dumps(obj))
        else:
            # Convert other types to string
            return meta.Datum(type='string', value=str(obj))
