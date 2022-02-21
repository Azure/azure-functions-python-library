#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Dict

from azure.functions.decorators.constants import QUEUE_TRIGGER, QUEUE
from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class QueueTrigger(Trigger):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: DataType):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return QUEUE_TRIGGER

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "queueName": self.queue_name,
            "connection": self.connection
        }


class QueueOutput(OutputBinding):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: DataType):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name() -> str:
        return QUEUE

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "queueName": self.queue_name,
            "connection": self.connection
        }
