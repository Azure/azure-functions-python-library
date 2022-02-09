#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Dict

from azure.functions.decorators.core import Trigger, DataType, OutputBinding
from azure.functions.decorators import Cardinality


class EventHubTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
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
    def connection(self) -> str:
        return self._connection

    @property
    def event_hub_name(self) -> str:
        return self._event_hub_name

    @property
    def cardinality(self) -> Cardinality:
        return self._cardinality

    @property
    def consumer_group(self) -> str:
        return self._consumer_group

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "dataType": self._data_type.name,
            "connection": self.connection,
            "eventHubName": self.event_hub_name,
            "cardinality": str(self.cardinality),
            "consumerGroup": self.consumer_group
        }


class EventHubOutput(OutputBinding):

    @staticmethod
    def get_binding_name() -> str:
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
    def connection(self) -> str:
        return self._connection

    @property
    def event_hub_name(self) -> str:
        return self._event_hub_name

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self._name,
            "dataType": self._data_type.name,
            "connection": self.connection,
            "eventHubName": self.event_hub_name
        }
