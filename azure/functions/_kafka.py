# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
from . import _abc, meta


class KafkaEvent(_abc.KafkaEvent):
    """A concrete implementation of Kafka event message type."""

    def __init__(self, *,
                 body: bytes,
                 trigger_metadata: typing.Optional[
                     typing.Mapping[str, meta.Datum]] = None,
                 key: typing.Optional[str] = None,
                 offset: typing.Optional[int] = None,
                 partition: typing.Optional[int] = None,
                 topic: typing.Optional[str] = None,
                 timestamp: typing.Optional[str] = None,
                 headers: typing.Optional[list] = None) -> None:
        self.__body = body
        self.__trigger_metadata = trigger_metadata
        self.__key = key
        self.__offset = offset
        self.__partition = partition
        self.__topic = topic
        self.__timestamp = timestamp
        self.__headers = headers

        # Cache for trigger metadata after Python object conversion
        self._trigger_metadata_pyobj: typing.Optional[
            typing.Mapping[str, typing.Any]] = None

    def get_body(self) -> bytes:
        return self.__body

    @property
    def key(self) -> typing.Optional[str]:
        return self.__key

    @property
    def offset(self) -> typing.Optional[int]:
        return self.__offset

    @property
    def partition(self) -> typing.Optional[int]:
        return self.__partition

    @property
    def topic(self) -> typing.Optional[str]:
        return self.__topic

    @property
    def timestamp(self) -> typing.Optional[str]:
        return self.__timestamp

    @property
    def headers(self) -> typing.Optional[list]:
        return self.__headers

    @property
    def metadata(self) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        if self.__trigger_metadata is None:
            return None

        if self._trigger_metadata_pyobj is None:
            self._trigger_metadata_pyobj = {}

            for k, v in self.__trigger_metadata.items():
                self._trigger_metadata_pyobj[k] = v.value

        return self._trigger_metadata_pyobj

    def __repr__(self) -> str:
        return (
            f'<azure.KafkaEvent '
            f'key={self.key} '
            f'partition={self.offset} '
            f'offset={self.offset} '
            f'topic={self.topic} '
            f'timestamp={self.timestamp} '
            f'at 0x{id(self):0x}>'
        )