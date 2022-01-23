#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class QueueTrigger(Trigger):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name():
        return "queueTrigger"

    def get_dict_repr(self):
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
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name():
        return "queue"

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "queueName": self.queue_name,
            "connection": self.connection,
        }
