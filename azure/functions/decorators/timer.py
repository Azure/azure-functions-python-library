#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from azure.functions.decorators.core import Trigger, DataType


class TimerTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "timerTrigger"

    def __init__(self,
                 name: str,
                 schedule: str,
                 data_type: DataType,
                 run_on_startup: bool,
                 use_monitor: bool) -> None:
        self._schedule = schedule
        self._run_on_startup = run_on_startup
        self._use_monitor = use_monitor
        super().__init__(name=name, data_type=data_type)

    @property
    def schedule(self):
        return self._schedule

    @property
    def run_on_startup(self):
        return self._run_on_startup

    @property
    def use_monitor(self):
        return self._use_monitor

    def get_dict_repr(self):
        return {
            "name": self.name,
            "type": self.type,
            "dataType": self._data_type.name,
            "direction": self._direction.name,
            "schedule": self.schedule,
            "runOnStartup": self.run_on_startup,
            "useMonitor": self.use_monitor
        }
