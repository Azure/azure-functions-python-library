# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
from typing import Optional

from azure.functions import _abc as azf_abc


class InputStream(azf_abc.InputStream):
    """An InputStream object.

    :param str name:
        An optional str specifying the name of the blob.

    :param str uri:
        An optional str specifying the uri of the blob.

    :param str length:
        An optional int specifying the length of the blob.
    """
    def __init__(self, *,
                 name: Optional[str] = None,
                 uri: Optional[str] = None,
                 length: Optional[int] = None) -> None:
        self._name = name
        self._length = length
        self._uri = uri

    @property
    def name(self) -> Optional[str]:
        """The name of the blob."""
        return self._name

    @property
    def length(self) -> Optional[int]:
        """The size of the blob in bytes."""
        return self._length

    @property
    def uri(self) -> Optional[str]:
        """The blob's primary location URI."""
        return self._uri

    def read(self, size=-1) -> bytes:
        """Return and read up to *size* bytes.

        :param int size:
            The number of bytes to read.  If the argument is omitted,
            ``None``, or negative, data is read and returned until
            EOF is reached.

        :return:
            Bytes read from the input stream.
        """
        return self._io.read(size)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return a JSON-safe dictionary of blob metadata fields.

        Blob content is intentionally excluded; use :meth:`read` to access it.
        """
        return {
            'name': self._name,
            'uri': self._uri,
            'length': self._length,
        }
