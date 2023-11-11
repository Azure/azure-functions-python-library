# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import io
import json
import os
from typing import Any, Optional, Union

from azure.functions import _abc as azf_abc
from . import meta


class ConnectionInfo(azf_abc.ConnectionInfo):
    def __init__(self, *, 
                 version: Optional[str] = None,
                 source: Optional[str] = None,
                 content_type: Optional[str] = None,
                 content: Optional[str] = None,
                 connection: Optional[str] = None,
                 container_name: Optional[str] = None,
                 blob_name: Optional[str] = None,
                 ) -> None:
        self._version = version
        self._source = source
        self._content_type = content_type
        self._content = content
        self._connection = connection
        self._container_name = container_name
        self._blob_name = blob_name

    @property
    def version(self) -> Optional[str]:
        return self._version

    @property
    def source(self) -> Optional[str]:
        return self._source

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type

    @property
    def content(self)-> Optional[str]:
        return self._content

    @property
    def connection(self)-> Optional[str]:
        return self._connection
    
    @property
    def container_name(self)-> Optional[str]:
        return self._container_name
    
    @property
    def blob_name(self)-> Optional[str]:
        return self._blob_name

class ConnectionInfoConverter(meta.InConverter,
                    meta.OutConverter,
                    binding='blob',
                    trigger='blobTrigger'):
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (azf_abc.ConnectionInfo, bytes, str))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return (
            issubclass(pytype, (str, bytes, bytearray, azf_abc.ConnectionInfo))
            or callable(getattr(pytype, 'read', None))
        )

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if callable(getattr(obj, 'read', None)):
            # file-like object
            obj = obj.read()

        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))

        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> Any:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type == 'model_binding_data':
            data = data.value
        else:
            raise ValueError(
                f'unexpected type of data received for the "blob" binding '
                f': {data_type!r}'
            )

        if not trigger_metadata:
            return ConnectionInfo(data=data)
        else:
            # properties = cls._decode_trigger_metadata_field(
            #     trigger_metadata, 'Properties', python_type=dict)
            # if properties:
            #     blob_properties = properties
            #     length = properties.get('Length')
            #     length = int(length) if length else None
            # else:
            #     blob_properties = None
            #     length = None

            # metadata = None
            # try:
            #     metadata = cls._decode_trigger_metadata_field(trigger_metadata,
            #                                                   'Metadata',
            #                                                   python_type=dict)
            # except (KeyError, ValueError):
            #     # avoiding any exceptions when fetching Metadata as the
            #     # metadata type is unclear.
            #     pass

            # decoding content
            content_json = json.loads(data.content)
            connection_string = os.getenv(content_json['Connection'])
            content_json['Connection'] = connection_string

            return ConnectionInfo(
                version=data.version,
                source=data.source,
                content_type=data.content_type,
                content=content_json,
                connection=content_json["Connection"],
                container_name=content_json["ContainerName"],
                blob_name=content_json["BlobName"]
            )
