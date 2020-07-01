# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import typing

from azure.functions import _servicebus as azf_sbus

from . import meta


class ServiceBusMessage(azf_sbus.ServiceBusMessage):
    """An HTTP response object."""

    def __init__(
            self, *,
            body: bytes,
            trigger_metadata: typing.Mapping[str, typing.Any] = None,
            content_type: typing.Optional[str] = None,
            correlation_id: typing.Optional[str] = None,
            delivery_count: typing.Optional[int] = 0,
            enqueued_time_utc: typing.Optional[datetime.datetime] = None,
            expiration_time: typing.Optional[datetime.datetime] = None,
            expires_at_utc: typing.Optional[datetime.datetime] = None,
            label: typing.Optional[str] = None,
            message_id: str,
            partition_key: typing.Optional[str] = None,
            reply_to: typing.Optional[str] = None,
            reply_to_session_id: typing.Optional[str] = None,
            scheduled_enqueue_time: typing.Optional[datetime.datetime] = None,
            session_id: typing.Optional[str] = None,
            time_to_live: typing.Optional[datetime.timedelta] = None,
            to: typing.Optional[str] = None,
            user_properties: typing.Dict[str, object]) -> None:

        self.__body = body
        self.__trigger_metadata = trigger_metadata
        self.__content_type = content_type
        self.__correlation_id = correlation_id
        self.__delivery_count = delivery_count
        self.__enqueued_time_utc = enqueued_time_utc
        self.__expiration_time = expiration_time
        self.__expires_at_utc = expires_at_utc
        self.__label = label
        self.__message_id = message_id
        self.__partition_key = partition_key
        self.__reply_to = reply_to
        self.__reply_to_session_id = reply_to_session_id
        self.__scheduled_enqueue_time = scheduled_enqueue_time
        self.__session_id = session_id
        self.__time_to_live = time_to_live
        self.__to = to
        self.__user_properties = user_properties

        # Cache for trigger metadata after Python object conversion
        self._trigger_metadata_pyobj: typing.Optional[
            typing.Mapping[str, typing.Any]] = None

    def get_body(self) -> bytes:
        return self.__body

    @property
    def content_type(self) -> typing.Optional[str]:
        return self.__content_type

    @property
    def correlation_id(self) -> typing.Optional[str]:
        return self.__correlation_id

    @property
    def delivery_count(self) -> typing.Optional[int]:
        return self.__delivery_count

    @property
    def enqueued_time_utc(self) -> typing.Optional[datetime.datetime]:
        return self.__enqueued_time_utc

    @property
    def expiration_time(self) -> typing.Optional[datetime.datetime]:
        return self.__expiration_time

    @property
    def expires_at_utc(self) -> typing.Optional[datetime.datetime]:
        return self.__expires_at_utc

    @property
    def label(self) -> typing.Optional[str]:
        return self.__label

    @property
    def message_id(self) -> str:
        return self.__message_id

    @property
    def partition_key(self) -> typing.Optional[str]:
        return self.__partition_key

    @property
    def reply_to(self) -> typing.Optional[str]:
        return self.__reply_to

    @property
    def reply_to_session_id(self) -> typing.Optional[str]:
        return self.__reply_to_session_id

    @property
    def scheduled_enqueue_time(self) -> typing.Optional[datetime.datetime]:
        return self.__scheduled_enqueue_time

    @property
    def session_id(self) -> typing.Optional[str]:
        return self.__session_id

    @property
    def time_to_live(self) -> typing.Optional[datetime.timedelta]:
        return self.__time_to_live

    @property
    def to(self) -> typing.Optional[str]:
        return self.__to

    @property
    def user_properties(self) -> typing.Dict[str, object]:
        return self.__user_properties

    @property
    def metadata(self) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        """Getting read-only trigger metadata in a Python dictionary.

        Exposing the raw trigger_metadata to our customer. For cardinality=many
        scenarios, each event points to the common metadata of all the events.

        So when using metadata field when cardinality=many, it only needs to
        take one of the events to get all the data (e.g. events[0].metadata).

        Returns:
        --------
        typing.Mapping[str, object]
            Return the Python dictionary of trigger metadata
        """
        if self.__trigger_metadata is None:
            return None

        if self._trigger_metadata_pyobj is None:
            # No need to do deepcopy since datum.python_value will construct
            # new object
            self._trigger_metadata_pyobj = {
                k: v.python_value for (k, v) in self.__trigger_metadata.items()
            }
        return self._trigger_metadata_pyobj

    def __repr__(self) -> str:
        return (
            f'<azure.functions.ServiceBusMessage '
            f'message_id={self.message_id} '
            f'at 0x{id(self):0x}>'
        )


class ServiceBusMessageInConverter(meta.InConverter,
                                   binding='serviceBusTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, azf_sbus.ServiceBusMessage)

    @classmethod
    def decode(cls, data: meta.Datum, *,
               trigger_metadata) -> ServiceBusMessage:

        if data is None:
            # ServiceBus message with no payload are possible.
            # See Azure/azure-functions-python-worker#330
            body = b''

        elif data.type in ['string', 'json']:
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        else:
            raise NotImplementedError(
                f'unsupported queue payload type: {data.type}')

        if trigger_metadata is None:
            raise NotImplementedError(
                f'missing trigger metadata for ServiceBus message input')

        return ServiceBusMessage(
            body=body,
            trigger_metadata=trigger_metadata,
            content_type=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ContentType', python_type=str),
            correlation_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'CorrelationId', python_type=str),
            delivery_count=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeliveryCount', python_type=int),
            enqueued_time_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'EnqueuedTimeUtc'),
            expiration_time=cls._parse_datetime_metadata(
                trigger_metadata, 'ExpirationTime'),
            expires_at_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'ExpiresAtUtc'),
            label=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Label', python_type=str),
            message_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'MessageId', python_type=str),
            partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PartitionKey', python_type=str),
            reply_to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyTo', python_type=str),
            reply_to_session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyToSessionId', python_type=str),
            scheduled_enqueue_time=cls._parse_datetime_metadata(
                trigger_metadata, 'ScheduledEnqueueTime'),
            session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SessionId', python_type=str),
            time_to_live=cls._parse_timedelta_metadata(
                trigger_metadata, 'TimeToLive'),
            to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'To', python_type=str),
            user_properties=cls._decode_trigger_metadata_field(
                trigger_metadata, 'UserProperties', python_type=dict),
        )


class ServiceBusMessageOutConverter(meta.OutConverter, binding='serviceBus'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes))

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            return meta.Datum(type='bytes', value=obj)

        raise NotImplementedError
