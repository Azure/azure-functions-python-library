#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from azure.functions.decorators.core import Trigger


class TimerTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "timerTrigger"

    def __init__(self,
                 name,
                 schedule,
                 run_on_startup = None,
                 use_monitor = None) -> None:
        self.schedule = schedule
        self.run_on_startup = run_on_startup
        self.use_monitor = use_monitor
        super().__init__(name=name)

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "schedule": self.schedule,
            "runOnStartup": self.runOnStartup,
            "useMonitor": self.use_monitor,
            "name": self.name
        }
