# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import io
from typing import Optional, Union

from azure.functions import _abc as azf_abc
from . import meta


class InputStream(azf_abc.InputStream):
    def __init__(self, *, data: Union[bytes, meta.Datum],
                 name: Optional[str] = None,
                 uri: Optional[str] = None,
                 length: Optional[int] = None,
                 blob_properties: Optional[dict] = None,
                 metadata: Optional[dict] = None) -> None:
        self._io = io.BytesIO(data)  # type: ignore
        self._name = name
        self._length = length
        self._uri = uri
        self._blob_properties = blob_properties
        self._metadata = metadata

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def length(self) -> Optional[int]:
        return self._length

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    @property
    def blob_properties(self):
        return self._blob_properties

    @property
    def metadata(self):
        return self._metadata

    def read(self, size=-1) -> bytes:
        return self._io.read(size)

    # implemented read1 method using aliasing.
    read1 = read

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return False