#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import QUEUE_TRIGGER, QUEUE
from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class QueueTrigger(Trigger):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: Optional[DataType] = None):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return QUEUE_TRIGGER


class QueueOutput(OutputBinding):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: Optional[DataType] = None):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return QUEUE
