import json
import typing

from azure.functions import _eventhub

from . import meta


class EventHubConverter(meta.InConverter, meta.OutConverter,
                        binding='eventHub'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        valid_types = (_eventhub.EventHubEvent)
        return (
            meta.is_iterable_type_annotation(pytype, valid_types)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        valid_types = (str, bytes)
        return (
            meta.is_iterable_type_annotation(pytype, str)
            or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> typing.Union[_eventhub.EventHubEvent,
                      typing.List[_eventhub.EventHubEvent]]:
        data_type = data.type

        if (data_type == 'string' or data_type == 'bytes'
                or data_type == 'json'):
            return cls.decode_single_event(data, trigger_metadata)

        elif (data_type == 'collection_bytes'
                or data_type == 'collection_string'):
            return cls.decode_multiple_events(data, trigger_metadata)

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(cls, data,
                            trigger_metadata) -> _eventhub.EventHubEvent:
        if data.type == 'string':
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        elif data.type == 'json':
            body = data.value.encode('utf-8')

        return _eventhub.EventHubEvent(body=body)

    @classmethod
    def decode_multiple_events(
            cls, data, trigger_metadata
    ) -> typing.List[_eventhub.EventHubEvent]:
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        events = []
        for i in range(len(parsed_data)):
            event = _eventhub.EventHubEvent(body=parsed_data[i])
            events.append(event)

        return events

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]
               ) -> meta.Datum:
        data = meta.Datum(type=None, value=None)

        if isinstance(obj, str):
            data = meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            data = meta.Datum(type='bytes', value=obj)

        elif isinstance(obj, int):
            data = meta.Datum(type='int', value=obj)

        elif isinstance(obj, list):
            data = meta.Datum(type='json', value=json.dumps(obj))

        return data


class EventHubTriggerConverter(EventHubConverter,
                               binding='eventHubTrigger', trigger=True):
    @classmethod
    def decode(
        cls, data: meta.Datum, *, trigger_metadata
    ) -> typing.Union[_eventhub.EventHubEvent,
                      typing.List[_eventhub.EventHubEvent]]:
        data_type = data.type

        if (data_type == 'string' or data_type == 'bytes'
                or data_type == 'json'):
            return cls.decode_single_event(data, trigger_metadata)

        elif (data_type == 'collection_bytes'
                or data_type == 'collection_string'):
            return cls.decode_multiple_events(data, trigger_metadata)

        else:
            raise NotImplementedError(
                f'unsupported event data payload type: {data_type}')

    @classmethod
    def decode_single_event(cls, data,
                            trigger_metadata) -> _eventhub.EventHubEvent:
        if data.type == 'string':
            body = data.value.encode('utf-8')

        elif data.type == 'bytes':
            body = data.value

        elif data.type == 'json':
            body = data.value.encode('utf-8')

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

    @classmethod
    def decode_multiple_events(
            cls, data, trigger_metadata
    ) -> typing.List[_eventhub.EventHubEvent]:
        if data.type == 'collection_bytes':
            parsed_data = data.value.bytes

        elif data.type == 'collection_string':
            parsed_data = data.value.string

        sys_props = trigger_metadata.get('SystemPropertiesArray')

        parsed_sys_props = json.loads(sys_props.value)

        if len(parsed_data) != len(parsed_sys_props):
            raise AssertionError('Number of bodies and metadata mismatched')

        events = []
        for i in range(len(parsed_data)):
            enqueued_time = parsed_sys_props[i].get('EnqueuedTimeUtc')
            partition_key = cls.encode(
                parsed_sys_props[i].get('PartitionKey'),
                expected_type=str)
            sequence_number = cls.encode(
                parsed_sys_props[i].get('SequenceNumber'),
                expected_type=int)
            offset = cls.encode(
                parsed_sys_props[i].get('Offset'),
                expected_type=int)

            event = _eventhub.EventHubEvent(
                body=parsed_data[i],
                enqueued_time=cls._parse_datetime(enqueued_time),
                partition_key=cls._decode_typed_data(
                    partition_key, python_type=str),
                sequence_number=cls._decode_typed_data(
                    sequence_number, python_type=int),
                offset=cls._decode_typed_data(
                    offset, python_type=int),
                iothub_metadata={}
            )

            events.append(event)

        return events
