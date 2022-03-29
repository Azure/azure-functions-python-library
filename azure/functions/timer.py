import json
import typing

from azure.functions import _abc as azf_abc
from . import meta


class TimerRequest(azf_abc.TimerRequest):

    def __init__(self, *, past_due: bool, schedulestatus: dict,
                 schedule: dict) -> None:
        self.__past_due = past_due
        self.__schedulestatus = schedulestatus
        self.__schedule = schedule

    @property
    def past_due(self):
        return self.__past_due

    @property
    def schedulestatus(self):
        return self.__schedulestatus

    @property
    def schedule(self):
        return self.__schedule


class TimerRequestConverter(meta.InConverter,
                            binding='timerTrigger', trigger=True):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, azf_abc.TimerRequest)

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        if data.type != 'json':
            raise NotImplementedError

        info = json.loads(data.value)

        return TimerRequest(
            past_due=info.get('IsPastDue', False),
            schedulestatus=info["ScheduleStatus"],
            schedule=info["Schedule"])
