import json
import typing

from azure.functions import _eventhub

from . import meta


class EventHubConverter(meta.InConverter, meta.OutConverter,
                        binding='eventHub'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, _eventhub.EventHubEvent)

    @classmethod
    def check_output_type_annotation(cls, pytype) -> bool:
        return (
            issubclass(pytype, (str, bytes))
            or (issubclass(pytype, typing.List)
                and issubclass(pytype.__args__[0], str))
        )

    @classmethod
    def decode(cls, data: meta.Datum, *,
               trigger_metadata) -> _eventhub.EventHubEvent:
        data_type = data.type

        if data_type == 'string':
            body = data.value.encode('utf-8')

        elif data_type == 'bytes':
            body = data.value

        elif data_type == 'json':
            body = data.value.encode('utf-8')

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

        return _eventhub.EventHubEvent(body=body)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            data = meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            data = meta.Datum(type='bytes', value=obj)

        elif isinstance(obj, list):
            data = meta.Datum(type='json', value=json.dumps(obj))

        return data


class EventHubTriggerConverter(EventHubConverter,
                               binding='eventHubTrigger', trigger=True):

    @classmethod
    def decode(cls, data: meta.Datum, *,
               trigger_metadata) -> _eventhub.EventHubEvent:
        data_type = data.type

        if data_type == 'string':
            body = data.value.encode('utf-8')

        elif data_type == 'bytes':
            body = data.value

        elif data_type == 'json':
            body = data.value.encode('utf-8')

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

        iothub_metadata = {}
        for f in trigger_metadata:
            if f.startswith('iothub-'):
                v = cls._decode_trigger_metadata_field(
                    trigger_metadata, f, python_type=str)
                iothub_metadata[f[len('iothub-'):]] = v

        return _eventhub.EventHubEvent(
            body=body,
            enqueued_time=cls._parse_datetime_metadata(
                trigger_metadata, 'EnqueuedTime'),
            partition_key=cls._decode_trigger_metadata_field(
                trigger_metadata, 'PartitionKey', python_type=str),
            sequence_number=cls._decode_trigger_metadata_field(
                trigger_metadata, 'SequenceNumber', python_type=int),
            offset=cls._decode_trigger_metadata_field(
                trigger_metadata, 'Offset', python_type=str),
            iothub_metadata=iothub_metadata
        )
