import collections
import datetime
import json

import typing

from azure.functions import _eventgrid as azf_eventgrid

from . import meta
from .meta import Datum


class EventGridEventInConverter(meta.InConverter, binding='eventGridTrigger',
                                trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        """
        Event Grid always sends an array and may send more than one event in the array.
        The runtime invokes function once for each array element, thus no need to parse List[EventGridEvent]
        """
        valid_types = azf_eventgrid.EventGridEvent
        return (
            isinstance(pytype, type) and issubclass(pytype, valid_types)
        )

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> azf_eventgrid.EventGridEvent:
        data_type = data.type

        if data_type == 'json':
            body = json.loads(data.value)
        else:
            raise NotImplementedError(
                f'unsupported event grid payload type: {data_type}')

        return azf_eventgrid.EventGridEvent(
            id=body.get('id'),
            topic=body.get('topic'),
            subject=body.get('subject'),
            event_type=body.get('eventType'),
            event_time=cls._parse_datetime(body.get('eventTime')),
            data=body.get('data'),
            data_version=body.get('dataVersion'),
        )


class EventGridOutConverter(meta.OutConverter, binding="eventGrid"):
    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        valid_types = (str, bytes, azf_eventgrid.EventGridEvent,
                       typing.List[azf_eventgrid.EventGridEvent])
        return (
                meta.is_iterable_type_annotation(pytype, str) or
                meta.is_iterable_type_annotation(pytype, azf_eventgrid.EventGridEvent)
                or (isinstance(pytype, type) and issubclass(pytype, valid_types))
        )

    @classmethod
    def encode(cls, obj: typing.Any, *, expected_type: typing.Optional[type]) -> typing.Optional[Datum]:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, bytes):
            return meta.Datum(type='bytes', value=obj)

        elif isinstance(obj, azf_eventgrid.EventGridEvent):
            return meta.Datum(
                type='json',
                value=json.dumps({
                    'id': obj.id,
                    'subject': obj.subject,
                    'dataVersion': obj.data_version,
                    'eventType': obj.event_type,
                    'data': obj.get_json(),
                    'eventTime': obj.event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })
            )

        elif isinstance(obj, collections.abc.Iterable):
            msgs = []
            for item in obj:
                if isinstance(item, str):
                    msgs.append(item)
                elif isinstance(item, azf_eventgrid.EventGridEvent):
                    msgs.append({
                        'id': item.id,
                        'subject': item.subject,
                        'dataVersion': item.data_version,
                        'eventType': item.event_type,
                        'data': item.get_json(),
                        'eventTime': item.event_time
                    })
                else:
                    raise NotImplementedError(
                        'invalid data type in output '
                        'queue message list: {}'.format(type(item)))

            return meta.Datum(
                type='json',
                value=json.dumps(msgs)
            )

        raise NotImplementedError

    @classmethod
    def _format_datetime(cls, dt: typing.Optional[datetime.datetime]):
        if dt is None:
            return None
        else:
            return dt.isoformat()
