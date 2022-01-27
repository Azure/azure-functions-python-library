#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, DataType, OutputBinding
from azure.functions.decorators.servicebus import Cardinality


class EventHubTrigger(Trigger):

    @staticmethod
    def get_binding_name():
        return "eventHubTrigger"

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: DataType,
                 cardinality: Cardinality,
                 consumer_group: str):
        self._connection = connection
        self._event_hub_name = event_hub_name
        self._cardinality = cardinality
        self._consumer_group = consumer_group
        super().__init__(name=name, data_type=data_type)

    @property
    def connection(self):
        return self._connection

    @property
    def event_hub_name(self):
        return self._event_hub_name

    @property
    def cardinality(self):
        return self._cardinality

    @property
    def consumer_group(self):
        return self._consumer_group

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "data_type": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name,
            "cardinality": str(self.cardinality),
            "consumerGroup": self.consumer_group
        }


class EventHubOutput(OutputBinding):

    @staticmethod
    def get_binding_name():
        return "eventHub"

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: DataType):
        self._connection = connection
        self._event_hub_name = event_hub_name
        super().__init__(name=name, data_type=data_type)

    @property
    def connection(self):
        return self._connection

    @property
    def event_hub_name(self):
        return self._event_hub_name

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self._name,
            "dataType": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name
        }