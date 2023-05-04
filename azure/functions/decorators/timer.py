#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import TIMER_TRIGGER
from azure.functions.decorators.core import Trigger, DataType


class TimerTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return TIMER_TRIGGER

    def __init__(self,
                 name: str,
                 schedule: str,
                 run_on_startup: Optional[bool] = None,
                 use_monitor: Optional[bool] = None,
                 retry_strategy: Optional[str] = None,
                 retry_max_retry_count: Optional[int] = None,
                 retry_delay_interval: Optional[str] = None,
                 retry_minimum_interval: Optional[str] = None,
                 retry_maximum_interval: Optional[str] = None,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        self.schedule = schedule
        self.run_on_startup = run_on_startup
        self.use_monitor = use_monitor
        self.retry_strategy = retry_strategy
        self.retry_max_retry_count = retry_max_retry_count
        self.retry_delay_interval = retry_delay_interval
        self.retry_minimum_interval = retry_minimum_interval
        self.retry_maximum_interval = retry_maximum_interval

        super().__init__(name=name, data_type=data_type)
