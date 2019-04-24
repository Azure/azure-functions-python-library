import datetime
import typing

from azure.functions import _abc as azf_abc

class KafkaEvent(azf_abc.KafkaEvent):
    """A concrete implementation of Kafka event message type."""

    def __init__(self, *,
                 body: bytes,
                 key: typing.Optional[str]=None,
                 offset: typing.Optional[int]=None,
                 partition: typing.Optional[int]=None,
                 topic: typing.Optional[str]=None,
                 timestamp: typing.Optional[str]=None) -> None:
        self.__body = body
        self.__key = key
        self.__offset = offset
        self.__partition = partition
        self.__topic = topic
        self.__timestamp = timestamp
    
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
