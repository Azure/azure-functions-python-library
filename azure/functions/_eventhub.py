import datetime
import typing

from azure.functions import _abc as funcabc


class EventHubEvent(funcabc.EventHubEvent):
    """A concrete implementation of Event Hub message type."""

    def __init__(self, *,
                 body: bytes,
                 enqueued_time: typing.Optional[datetime.datetime] = None,
                 partition_key: typing.Optional[str] = None,
                 sequence_number: typing.Optional[int] = None,
                 offset: typing.Optional[str] = None,
                 iothub_metadata: typing.Optional[
                     typing.Mapping[str, str]] = None) -> None:
        self.__body = body
        self.__enqueued_time = enqueued_time
        self.__partition_key = partition_key
        self.__sequence_number = sequence_number
        self.__offset = offset
        self.__iothub_metadata = iothub_metadata

    def get_body(self) -> bytes:
        return self.__body

    @property
    def partition_key(self) -> typing.Optional[str]:
        return self.__partition_key

    @property
    def iothub_metadata(self) -> typing.Optional[typing.Mapping[str, str]]:
        return self.__iothub_metadata

    @property
    def sequence_number(self) -> typing.Optional[int]:
        return self.__sequence_number

    @property
    def enqueued_time(self) -> typing.Optional[datetime.datetime]:
        return self.__enqueued_time

    @property
    def offset(self) -> typing.Optional[str]:
        return self.__offset

    def __repr__(self) -> str:
        return (
            f'<azure.EventHubEvent '
            f'partition_key={self.partition_key} '
            f'sequence_number={self.sequence_number} '
            f'enqueued_time={self.enqueued_time} '
            f'at 0x{id(self):0x}>'
        )
