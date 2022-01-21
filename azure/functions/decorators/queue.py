#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, OutputBinding


class QueueTrigger(Trigger):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: Optional[str] = None):
        self.data_type = data_type
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name)

    @staticmethod
    def get_binding_name():
        return "queueTrigger"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
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
                 data_type: Optional[str] = None):
        self.data_type = data_type
        self.queue_name = queue_name
        self.connection = connection
        super().__init__(name=name)

    @staticmethod
    def get_binding_name():
        return "queue"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "data_type": self.data_type,
            "queueName": self.queue_name,
            "connection": self.connection,
        }
