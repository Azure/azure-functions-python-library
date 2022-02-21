#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from azure.functions.decorators.constants import TIMER_TRIGGER
from azure.functions.decorators.core import Trigger, DataType


class TimerTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return TIMER_TRIGGER

    def __init__(self,
                 name: str,
                 schedule: str,
                 data_type: DataType,
                 run_on_startup: bool,
                 use_monitor: bool) -> None:
        self.schedule = schedule
        self.run_on_startup = run_on_startup
        self.use_monitor = use_monitor
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "dataType": self.data_type,
            "direction": self.direction,
            "schedule": self.schedule,
            "runOnStartup": self.run_on_startup,
            "useMonitor": self.use_monitor
        }
