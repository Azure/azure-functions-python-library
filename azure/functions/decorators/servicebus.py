#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Dict

from azure.functions.decorators import Cardinality, AccessRights
from azure.functions.decorators.constants import SERVICE_BUS_TRIGGER, \
    SERVICE_BUS
from azure.functions.decorators.core import Trigger, OutputBinding, DataType


class ServiceBusQueueTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: DataType,
                 access_rights: AccessRights,
                 is_sessions_enabled: bool,
                 cardinality: Cardinality):
        self.connection = connection
        self.queue_name = queue_name
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights.value,
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": self.cardinality.value
        }


class ServiceBusQueueOutput(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return SERVICE_BUS

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: DataType,
                 access_rights: AccessRights):
        self.connection = connection
        self.queue_name = queue_name
        self.access_rights = access_rights
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights.value
        }


class ServiceBusTopicTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return SERVICE_BUS_TRIGGER

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: DataType,
                 access_rights: AccessRights,
                 is_sessions_enabled: bool,
                 cardinality: Cardinality):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self) -> Dict:
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights.value,
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": self.cardinality.value
        }


class ServiceBusTopicOutput(OutputBinding):
    @staticmethod
    def get_binding_name():
        return SERVICE_BUS

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: DataType,
                 access_rights: AccessRights):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.access_rights = access_rights
        super().__init__(name=name, data_type=data_type)

    def get_dict_repr(self):
        return {
            "type": self.type,
            "direction": self.direction,
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights.value
        }
