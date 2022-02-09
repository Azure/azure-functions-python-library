#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Dict

from azure.functions.decorators import Cardinality, AccessRights
from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class ServiceBusQueueTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return "serviceBusTrigger"

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: DataType,
                 access_rights: AccessRights,
                 is_sessions_enabled: bool,
                 cardinality: Cardinality):
        self._connection = connection
        self._queue_name = queue_name
        self._access_rights = access_rights
        self._is_sessions_enabled = is_sessions_enabled
        self._cardinality = cardinality
        super().__init__(name=name, data_type=data_type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def connection(self) -> str:
        return self._connection

    @property
    def queue_name(self) -> str:
        return self._queue_name

    @property
    def access_rights(self) -> AccessRights:
        return self._access_rights

    @property
    def is_sessions_enabled(self) -> bool:
        return self._is_sessions_enabled

    @property
    def cardinality(self) -> Cardinality:
        return self._cardinality

    def get_dict_repr(self) -> dict:
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self._data_type.name,
            "accessRights": str(self.access_rights.value),
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": str(self.cardinality.value)
        }


class ServiceBusQueueOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "serviceBus"

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: DataType,
                 access_rights: AccessRights):
        self._connection = connection
        self._queue_name = queue_name
        self._access_rights = access_rights
        super().__init__(name=name, data_type=data_type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def connection(self) -> str:
        return self._connection

    @property
    def queue_name(self) -> str:
        return self._queue_name

    @property
    def access_rights(self) -> AccessRights:
        return self._access_rights

    def get_dict_repr(self) -> dict:
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self._data_type.name,
            "accessRights": str(self.access_rights.value)
        }


class ServiceBusTopicTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "serviceBusTrigger"

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: DataType,
                 access_rights: AccessRights,
                 is_sessions_enabled: bool,
                 cardinality: Cardinality):
        self._connection = connection
        self._topic_name = topic_name
        self._subscription_name = subscription_name
        self._access_rights = access_rights
        self._is_sessions_enabled = is_sessions_enabled
        self._cardinality = cardinality
        super().__init__(name=name, data_type=data_type)

    @property
    def connection(self) -> str:
        return self._connection

    @property
    def topic_name(self) -> str:
        return self._topic_name

    @property
    def subscription_name(self) -> str:
        return self._subscription_name

    @property
    def access_rights(self) -> AccessRights:
        return self._access_rights

    @property
    def is_sessions_enabled(self) -> bool:
        return self._is_sessions_enabled

    @property
    def cardinality(self) -> Cardinality:
        return self._cardinality

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self._data_type.name,
            "accessRights": str(self.access_rights.value),
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": str(self.cardinality.value)
        }


class ServiceBusTopicOutput(OutputBinding):
    @staticmethod
    def get_binding_name():
        return "serviceBus"

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: DataType,
                 access_rights: AccessRights):
        self._connection = connection
        self._topic_name = topic_name
        self._subscription_name = subscription_name
        self._access_rights = access_rights
        super().__init__(name=name, data_type=data_type)

    @property
    def connection(self):
        return self._connection

    @property
    def topic_name(self):
        return self._topic_name

    @property
    def subscription_name(self):
        return self._subscription_name

    @property
    def access_rights(self):
        return self._access_rights

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self._direction.name,
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self._data_type.name,
            "accessRights": str(self.access_rights.value)
        }
