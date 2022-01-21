#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, StringifyEnum, \
    OutputBinding


class AccessRights(StringifyEnum):
    MANAGE = "manage"
    LISTEN = "listen"


class Cardinality(StringifyEnum):
    ONE = "one"
    MANY = "many"


class ServiceBusQueueTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "serviceBusTrigger"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights,
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": self.cardinality
        }

    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: Optional[str] = None,
                 access_rights = AccessRights.MANAGE,
                 is_sessions_enabled: bool = False,
                 cardinality: Cardinality = Cardinality.ONE):
        self.connection = connection
        self.queue_name = queue_name
        self.data_type = data_type
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name)


class ServiceBusQueueOutput(OutputBinding):
    def __init__(self,
                 name: str,
                 connection: str,
                 queue_name: str,
                 data_type: Optional[str] = None,
                 access_rights = AccessRights.MANAGE):
        self.connection = connection
        self.queue_name = queue_name
        self.data_type = data_type
        self.access_rights = access_rights
        super().__init__(name=name)

    @staticmethod
    def get_binding_name():
        return "serviceBus"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "connection": self.connection,
            "queueName": self.queue_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights
        }


class ServiceBusTopicTrigger(Trigger):
    @staticmethod
    def get_binding_name():
        return "serviceBusTrigger"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights,
            "isSessionsEnabled": self.is_sessions_enabled,
            "cardinality": self.cardinality
        }

    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: Optional[str] = None,
                 access_rights = AccessRights.MANAGE,
                 is_sessions_enabled: bool = False,
                 cardinality: Cardinality = Cardinality.ONE):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.data_type = data_type
        self.access_rights = access_rights
        self.is_sessions_enabled = is_sessions_enabled
        self.cardinality = cardinality
        super().__init__(name=name)


class ServiceBusTopicOutput(OutputBinding):
    def __init__(self,
                 name: str,
                 connection: str,
                 topic_name: str,
                 subscription_name: str,
                 data_type: Optional[str] = None,
                 access_rights = AccessRights.MANAGE):
        self.connection = connection
        self.topic_name = topic_name
        self.subscription_name = subscription_name
        self.data_type = data_type
        self.access_rights = access_rights
        super().__init__(name=name)

    @staticmethod
    def get_binding_name():
        return "serviceBus"

    def get_dict_repr(self):
        return {
            "type": self.get_binding_name(),
            "direction": self.get_binding_direction(),
            "name": self.name,
            "connection": self.connection,
            "topicName": self.topic_name,
            "subscriptionName": self.subscription_name,
            "dataType": self.data_type,
            "accessRights": self.access_rights
        }
