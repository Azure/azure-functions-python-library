#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class QueueTrigger(Trigger):
    def __init__(self,
                 name: str,
                 queue_name: str,
                 connection: str,
                 data_type: DataType):
        self._queue_name = queue_name
        self._connection = connection
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name():
        return "queueTrigger"

    @property
    def queue_name(self):
        return self._queue_name

    @property
    def connection(self):
        return self._connection

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
                 data_type: DataType):
        self._queue_name = queue_name
        self._connection = connection
        super().__init__(name=name, data_type=data_type)

    @property
    def queue_name(self):
        return self._queue_name

    @property
    def connection(self):
        return self._connection

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
            "connection": self.connection
        }
