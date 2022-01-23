#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, DataType, OutputBinding
from azure.functions.decorators.servicebus import Cardinality


class EventHubTrigger(Trigger):

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: Optional[DataType] = DataType.UNDEFINED,
                 cardinality: Optional[Cardinality] = Cardinality.MANY,
                 consumer_group: Optional[str] = "$Default"):
        self.connection = connection
        self.event_hub_name = event_hub_name
        self.cardinality = cardinality
        self.consumer_group = consumer_group
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name():
        return "eventHubTrigger"

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "data_type": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name,
            "cardinality": self.cardinality,
            "consumerGroup": self.consumer_group
        }


class EventHubOutput(OutputBinding):

    def __init__(self,
                 name: str,
                 connection: str,
                 event_hub_name: str,
                 data_type: Optional[DataType] = DataType.UNDEFINED):
        self.connection = connection
        self.event_hub_name = event_hub_name
        super().__init__(name=name, data_type=data_type)

    @staticmethod
    def get_binding_name():
        return "eventHub"

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "dataType": self.data_type,
            "connection": self.connection,
            "eventHubName": self.event_hub_name
        }
