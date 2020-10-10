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
            dead_letter_source: Optional[str] = None,
            delivery_count: Optional[int] = None,
            enqueued_sequence_number: Optional[int] = None,
            enqueued_time_utc: Optional[datetime.datetime] = None,
            expires_at_utc: Optional[datetime.datetime] = None,
            force_persistence: Optional[bool] = None,
            label: Optional[str] = None,
            locked_until_utc: Optional[datetime.datetime] = None,
            lock_token: Optional[str] = None,
            message_id: str,
            partition_key: Optional[str] = None,
            reply_to: Optional[str] = None,
            reply_to_session_id: Optional[str] = None,
            scheduled_enqueue_time_utc: Optional[datetime.datetime] = None,
            sequence_number: Optional[int] = 0,
            session_id: Optional[str] = None,
            time_to_live: Optional[datetime.timedelta] = None,
            to: Optional[str] = None,
            via_partition_key: Optional[str] = None,
            user_properties: Dict[str, object]) -> None:

        self.__body = body
        self.__trigger_metadata = trigger_metadata
        self.__content_type = content_type
        self.__correlation_id = correlation_id
        self.__dead_letter_source = dead_letter_source
        self.__delivery_count = delivery_count
        self.__enqueued_sequence_number = enqueued_sequence_number
        self.__enqueued_time_utc = enqueued_time_utc
        self.__expires_at_utc = expires_at_utc
        self.__force_persistence = force_persistence
        self.__label = label
        self.__locked_until_utc = locked_until_utc
        self.__lock_token = lock_token
        self.__message_id = message_id
        self.__partition_key = partition_key
        self.__reply_to = reply_to
        self.__reply_to_session_id = reply_to_session_id
        self.__scheduled_enqueue_time_utc = scheduled_enqueue_time_utc
        self.__sequence_number = sequence_number
        self.__session_id = session_id
        self.__time_to_live = time_to_live
        self.__to = to
        self.__via_partition_key = via_partition_key
        self.__user_properties = user_properties

        # Cache for trigger metadata after Python object conversion
        self._trigger_metadata_pyobj: Optional[Mapping[str, Any]] = None

    def get_body(self) -> bytes:
        return self.__body

    @property
    def content_type(self) -> Optional[str]:
        return self.__content_type

    @property
    def correlation_id(self) -> Optional[str]:
        return self.__correlation_id

    @property
    def dead_letter_source(self) -> Optional[str]:
        return self.__dead_letter_source

    @property
    def delivery_count(self) -> Optional[int]:
        return self.__delivery_count

    @property
    def enqueued_sequence_number(self) -> Optional[int]:
        return self.__enqueued_sequence_number

    @property
    def enqueued_time_utc(self) -> Optional[datetime.datetime]:
        return self.__enqueued_time_utc

    @property
    def expires_at_utc(self) -> Optional[datetime.datetime]:
        return self.__expires_at_utc

    @property
    def expiration_time(self) -> Optional[datetime.datetime]:
        """(Deprecated) Use expires_at_utc instead"""
        return self.__expires_at_utc

    @property
    def force_persistence(self) -> Optional[bool]:
        return self.__force_persistence

    @property
    def label(self) -> Optional[str]:
        return self.__label

    @property
    def locked_until_utc(self) -> Optional[datetime.datetime]:
        return self.__locked_until_utc

    @property
    def lock_token(self) -> Optional[str]:
        return self.__lock_token

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
        """(Deprecated) Use scheduled_enqueue_time_utc instead"""
        return self.__scheduled_enqueue_time_utc

    @property
    def scheduled_enqueue_time_utc(self) -> Optional[datetime.datetime]:
        return self.__scheduled_enqueue_time_utc

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
    def via_partition_key(self) -> Optional[str]:
        return self.__via_partition_key

    @property
    def user_properties(self) -> Dict[str, object]:
        return self.__user_properties

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
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
        return issubclass(pytype, azf_sbus.ServiceBusMessage) or (
            meta.is_iterable_type_annotation(
                pytype, azf_sbus.ServiceBusMessage))

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
            return cls.decode_single_message(data,
                    trigger_metadata=trigger_metadata)
        elif cls._is_cardinality_many(trigger_metadata):
            return cls.decode_multiple_messages(data,
                    trigger_metadata=trigger_metadata)
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
            dead_letter_source=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeadLetterSource', python_type=str),
            delivery_count=cls._decode_trigger_metadata_field(
                trigger_metadata, 'DeliveryCount', python_type=int),
            enqueued_sequence_number=cls._decode_trigger_metadata_field(
                trigger_metadata, 'EnqueuedSequenceNumber', python_type=int),
            enqueued_time_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'EnqueuedTimeUtc'),
            expires_at_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'ExpiresAtUtc'),
            force_persistence=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ForcePersistence', python_type=bool),
            label=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Label', python_type=str),
            locked_until_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'LockedUntilUtc'),
            lock_token=cls._decode_trigger_metadata_field(
                trigger_metadata, 'LockToken', python_type=str),
            message_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'MessageId', python_type=str),
            partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PartitionKey', python_type=str),
            reply_to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyTo', python_type=str),
            reply_to_session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ReplyToSessionId', python_type=str),
            scheduled_enqueue_time_utc=cls._parse_datetime_metadata(
                trigger_metadata, 'ScheduledEnqueueTimeUtc'),
            session_id=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SessionId', python_type=str),
            time_to_live=cls._parse_timedelta_metadata(
                trigger_metadata, 'TimeToLive'),
            to=cls._decode_trigger_metadata_field(
                trigger_metadata, 'To', python_type=str),
            via_partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'ViaPartitionKey', python_type=str),
            user_properties=cls._decode_trigger_metadata_field(
                trigger_metadata, 'UserProperties', python_type=dict),
        )

    @classmethod
    def decode_multiple_messages(cls, data: meta.Datum, *,
        trigger_metadata: Mapping[str, meta.Datum]) -> List[ServiceBusMessage]:
        """Unlike EventHub, the trigger_metadata already contains a set of
        arrays (e.g. 'ContentTypeArray', 'CorrelationidArray'...). We can
        retrieve message properties directly from those array.
        """
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        # Input Trigger IotHub Event
        elif data.type == 'json':
            parsed_data = json.loads(data.value)

        return cls._extract_messages(parsed_data, data.type, trigger_metadata)

    @classmethod
    def _is_cardinality_many(cls, trigger_metadata) -> bool:
        return 'UserPropertiesArray' in trigger_metadata

    @classmethod
    def _is_cardinality_one(cls, trigger_metadata) -> bool:
        return 'UserProperties' in trigger_metadata

    @classmethod
    def _get_event_count(cls, trigger_metadata) -> int:
        datum = trigger_metadata['UserPropertiesArray']
        user_props = json.loads(datum.value)
        return len(user_props)

    @classmethod
    def _marshall_message_body(cls, parsed_data, data_type) -> bytes:
        if data_type == 'str':
            return parsed_data.encode('utf-8')

        if data_type == 'json':
            return json.dumps(parsed_data).encode('utf-8')

        return parsed_data

    @classmethod
    def _extract_messages(cls,
            parsed_data: str,
            data_type: type,
            trigger_metadata: Mapping[str, meta.Datum]
        ) -> List[ServiceBusMessage]:

        num_messages = cls._get_event_count(trigger_metadata)

        messages = []
        content_types: List[str] = (
            trigger_metadata['ContentTypeArray'].value.string
        )
        correlation_ids: List[str] = (
            trigger_metadata['CorrelationIdArray'].value.string
        )
        dead_letter_sources: List[str] = (
            trigger_metadata['DeadLetterSourceArray'].value.string
        )
        delivery_counts: List[int] = json.loads(
            trigger_metadata['DeliveryCountArray'].value
        )
        enqueued_time_utcs: List[str] = json.loads(
            trigger_metadata['EnqueuedTimeUtcArray'].value
        )
        expires_at_utcs: List[str] = json.loads(
            trigger_metadata['ExpiresAtUtcArray'].value
        )
        labels: List[str] = (
            trigger_metadata['LabelArray'].value.string
        )
        lock_tokens: List[str] = (
            trigger_metadata['LockTokenArray'].value.string
        )
        message_ids: List[str] = (
            trigger_metadata['MessageIdArray'].value.string
        )
        sequence_numbers: List[int] = (
            trigger_metadata['SequenceNumberArray'].value.sint64
        )
        tos: List[str] = (
            trigger_metadata['ToArray'].value.string
        )
        reply_tos: List[str] = (
            trigger_metadata['ReplyToArray'].value.string
        )
        user_properties_list: List[Dict[str, Any]] = json.loads(
            trigger_metadata['UserPropertiesArray'].value
        )

        for i in range(num_messages):
            messages.append(ServiceBusMessage(
                body=cls._marshall_message_body(parsed_data[i], data_type),
                trigger_metadata=trigger_metadata,
                content_type=cls._get_or_none(content_types, i),
                correlation_id=cls._get_or_none(correlation_ids, i),
                dead_letter_source=cls._get_or_none(dead_letter_sources, i),
                delivery_count=cls._get_or_none(delivery_counts, i),
                enqueued_time_utc=cls._parse_datetime(
                    cls._get_or_none(enqueued_time_utcs, i)),
                expires_at_utc=cls._parse_datetime(
                    cls._get_or_none(expires_at_utcs, i)),
                label=cls._get_or_none(labels, i),
                lock_token=cls._get_or_none(lock_tokens, i),
                message_id=cls._get_or_none(message_ids, i),
                sequence_number=cls._get_or_none(sequence_numbers, i),
                to=cls._get_or_none(tos, i),
                reply_to=cls._get_or_none(reply_tos, i),
                user_properties=cls._get_or_none(user_properties_list, i)
            ))
        return messages

    @classmethod
    def _get_or_none(cls, list_: List[Any], index: int) -> Any:
        """Some metadata array does not contain any values (e.g.
        correlation_ids array may be empty [] when there's multiple messages).

        This results in a IndexError when referencing the message. To avoid
        this issue, when getting the value, we should return None is index is
        out of bound.
        """
        if index >= len(list_):
            return None

        return list_[index]


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
