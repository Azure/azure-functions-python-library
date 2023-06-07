#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import DAPR_SERVICE_INVOCATION_TRIGGER, DAPR_BINDING_TRIGGER, DAPR_TOPIC_TRIGGER
from azure.functions.decorators.core import Trigger, DataType, OutputBinding, \
    Cardinality


class DaprServiceInvocationTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_SERVICE_INVOCATION_TRIGGER

    def __init__(self,
                 name: str,
                 method_name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.method_name = method_name
        super().__init__(name=name, data_type=data_type)

class DaprBindingTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_BINDING_TRIGGER

    def __init__(self,
                 name: str,
                 binding_name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.binding_name = binding_name
        super().__init__(name=name, data_type=data_type)

class DaprTopicTrigger(Trigger):

    @staticmethod
    def get_binding_name() -> str:
        return DAPR_TOPIC_TRIGGER

    def __init__(self,
                 name: str,
                 pub_sub_name: str,
                 topic: str,
                 route: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        self.pub_sub_name = pub_sub_name
        self.topic = topic
        self.route = route
        super().__init__(name=name, data_type=data_type)