# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing

from azure.functions import _abc as azf_abc


class TimerRequest(azf_abc.TimerRequest):

    def __init__(self, *, past_due: bool = False,
                 schedule_status: typing.Optional[dict] = None,
                 schedule: typing.Optional[dict] = None) -> None:
        self.__past_due = past_due
        self.__schedule_status = schedule_status if schedule_status else {}
        self.__schedule = schedule if schedule else {}

    @property
    def past_due(self) -> bool:
        return self.__past_due

    @property
    def schedule_status(self) -> dict:
        return self.__schedule_status

    @property
    def schedule(self) -> dict:
        return self.__schedule
