# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import json
from typing import Dict, Any, List, Union, Optional, Mapping

from azure.functions import _servicebus as azf_sbus

from . import meta


class ServiceBusMessage(azf_sbus.ServiceBusMessage):
    """An HTTP response object."""

    def __init__(
            self, *,
            body: bytes,
            trigger_metadata: Mapping[str, Any] = None,
            content_type: Optional[str] = None,
            correlation_id: Optional[str] = None,
            delivery_count: Optional[int] = 0,
            enqueued_time_utc: Optional[datetime.datetime] = None,
            expiration_time: Optional[datetime.datetime] = None,
            expires_at_utc: Optional[datetime.datetime] = None,
            label: Optional[str] = None,
            message_id: str,
            partition_key: Optional[str] = None,
            reply_to: Optional[str] = None,
            reply_to_session_id: Optional[str] = None,
            scheduled_enqueue_time: Optional[datetime.datetime] = None,
            session_id: Optional[str] = None,
            time_to_live: Optional[datetime.timedelta] = None,
            to: Optional[str] = None,
            user_properties: Dict[str, object]) -> None:

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
        self._trigger_metadata_pyobj: Optional[
            Mapping[str, Any]] = None

    def get_body(self) -> bytes:
        return self.__body

    @property
    def content_type(self) -> Optional[str]:
        return self.__content_type

    @property
    def correlation_id(self) -> Optional[str]:
        return self.__correlation_id

    @property
    def delivery_count(self) -> Optional[int]:
        return self.__delivery_count

    @property
    def enqueued_time_utc(self) -> Optional[datetime.datetime]:
        return self.__enqueued_time_utc

    @property
    def expiration_time(self) -> Optional[datetime.datetime]:
        return self.__expiration_time

    @property
    def expires_at_utc(self) -> Optional[datetime.datetime]:
        return self.__expires_at_utc

    @property
    def label(self) -> Optional[str]:
        return self.__label

    @property
    def message_id(self) -> str:
        return self.__message_id

    @property
    def partition_key(self) -> Optional[str]:
        return self.__partition_key

    @property
    def reply_to(self) -> Optional[str]:
        return self.__reply_to

    @property
    def reply_to_session_id(self) -> Optional[str]:
        return self.__reply_to_session_id

    @property
    def scheduled_enqueue_time(self) -> Optional[datetime.datetime]:
        return self.__scheduled_enqueue_time

    @property
    def session_id(self) -> Optional[str]:
        return self.__session_id

    @property
    def time_to_live(self) -> Optional[datetime.timedelta]:
        return self.__time_to_live

    @property
    def to(self) -> Optional[str]:
        return self.__to

    @property
    def user_properties(self) -> Dict[str, object]:
        return self.__user_properties

    @property
    def metadata(self) -> Optional[Mapping[str, Any]]:
        """Getting read-only trigger metadata in a Python dictionary.

        Exposing the raw trigger_metadata to our customer. For cardinality=many
        scenarios, each event points to the common metadata of all the events.

        So when using metadata field when cardinality=many, it only needs to
        take one of the events to get all the data (e.g. events[0].metadata).

        Returns:
        --------
        Mapping[str, object]
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
    def decode(
        cls, data: meta.Datum, *, trigger_metadata: Mapping[str, meta.Datum]
    ) -> Union[ServiceBusMessage, List[ServiceBusMessage]]:
        """Returns the application setting from environment variable.

        Parameters
        ----------
        data: meta.Datum
            The datum from GRPC message

        trigger_metadata: Mapping[str, meta.Datum]
            The metadata of the Service Bus trigger, usually populated by
            function host

        Returns
        -------
        Union[ServiceBusMessage, List[ServiceBusMessage]]
            When 'cardinality' is set to 'one', this method returns a single
            ServiceBusMessage. When 'cardinality' is set to 'many' this method
            returns a list of ServiceBusMessage.
        """
        if cls._is_cardinality_one(trigger_metadata):
            raise Exception('DECODE SINGLE MESSAGE')
            return cls.decode_single_message(data, trigger_metadata)
        elif cls._is_cardinality_many(trigger_metadata):
            raise Exception('DECODE MULTIPLE MESSAGE')
            return cls.decode_multiple_messages(data, trigger_metadata)
        else:
            raise NotImplementedError(
                f'unsupported service bus data type: {data.type}')

    @classmethod
    def decode_single_message(cls, data: meta.Datum, *,
        trigger_metadata: Mapping[str, meta.Datum]) -> ServiceBusMessage:
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

    @classmethod
    def decode_multiple_messages(cls, data: meta.Datum, *,
        trigger_metadata: Mapping[str, meta.Datum]) -> List[ServiceBusMessage]:
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        elif data.type == 'json':
            parsed_data = json.loads(data.value)

        sys_props = trigger_metadata.get('SystemPropertiesArray')

        parsed_sys_props: List[Any] = []
        if sys_props is not None:
            parsed_sys_props = json.loads(sys_props.value)

        messages = []
        for i in range(len(parsed_data)):
            enqueued_time = parsed_sys_props[i].get('EnqueuedTimeUtc')

            message = ServiceBusMessage(
                body=cls._marshall_message_body(parsed_data[i], data.type),
                trigger_metadata=trigger_metadata,
            )

            messages.append(message)

        return messages

    @classmethod
    def _is_cardinality_many(cls, trigger_metadata) -> bool:
        return 'SystemPropertiesArray' in trigger_metadata

    @classmethod
    def _is_cardinality_one(cls, trigger_metadata) -> bool:
        return 'SystemProperties' in trigger_metadata

    @classmethod
    def _marshall_message_body(cls, parsed_data, data_type) -> str:
        if data_type == 'bytes':
            return parsed_data.encode('utf-8')

        if data_type == 'json':
            return json.dumps(parsed_data).encode('utf-8')

        return parsed_data

class ServiceBusMessageOutConverter(meta.OutConverter, binding='serviceBus'):

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes))

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            return meta.Datum(type='bytes', value=obj)

        raise NotImplementedError
