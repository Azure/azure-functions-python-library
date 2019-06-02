import json
import typing

from azure.functions import _eventgrid

from . import meta


class EventGridEventInConverter(meta.InConverter,
                                binding='eventGridTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, _eventgrid.EventGridEvent)

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        data_type = data.type

        if data_type == 'json':
            body = json.loads(data.value)
        else:
            raise NotImplementedError(
                f'unsupported event grid payload type: {data_type}')

        if trigger_metadata is None:
            raise NotImplementedError(
                f'missing trigger metadata for event grid input')

        return _eventgrid.EventGridEvent(
            id=body.get('id'),
            topic=body.get('topic'),
            subject=body.get('subject'),
            event_type=body.get('eventType'),
            event_time=cls._parse_datetime(body.get('eventTime')),
            data=body.get('data'),
            data_version=body.get('dataVersion'),
        )
