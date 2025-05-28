# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import typing

from azure.functions import _abc as azf_abc
from azure.functions import _timer as azf_timer
from . import meta


class TimerRequest(azf_timer.TimerRequest):
    """A Timer request object."""

    def __init__(self, *, past_due: bool = False,
                 schedule_status: typing.Optional[dict] = None,
                 schedule: typing.Optional[dict] = None) -> None:
        super().__init__(past_due=past_due)
        self.__schedule_status = schedule_status if schedule_status else {}
        self.__schedule = schedule if schedule else {}

    @property
    def schedule_status(self) -> dict:
        return self.__schedule_status

    @property
    def schedule(self) -> dict:
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
            schedule_status=info.get('ScheduleStatus', {}),
            schedule=info.get('Schedule', {}))
