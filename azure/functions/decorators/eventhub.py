#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Dict

from azure.functions.decorators.constants import EVENT_HUB_TRIGGER, EVENT_HUB
from azure.functions.decorators.core import Trigger, DataType, OutputBinding
from azure.functions.decorators import Cardinality


class EventHubTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_HUB_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: DataType,
                 cardinality: Cardinality,
                 consumer_group: str):
        self.connection = connection
        self.event_hub_name = event_hub_name
        self.cardinality = cardinality
        self.consumer_group = consumer_group
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name,
            "cardinality": self.cardinality,
            "consumerGroup": self.consumer_group
        }


class EventHubOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
        return EVENT_HUB

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: DataType):
        self.connection = connection
        self.event_hub_name = event_hub_name
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name
        }
