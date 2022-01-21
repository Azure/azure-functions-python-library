#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, DataType


class TimerTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "timerTrigger"

    def __init__(self,
                 name: str,
                 schedule: str,
                 run_on_startup: Optional[bool] = None,
                 use_monitor: Optional[bool] = None,
                 data_type: Optional[DataType] = DataType.UNDEFINED) -> None:
        self.schedule = schedule
        self.run_on_startup = run_on_startup
        self.use_monitor = use_monitor
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        return {
            "name": self.name,
            "type": self.type,
            "dataType": self.data_type,
            "direction": self.direction,
            "schedule": self.schedule,
            "runOnStartup": self.run_on_startup,
            "useMonitor": self.use_monitor
        }
