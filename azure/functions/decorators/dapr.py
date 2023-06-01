#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import DAPR_SERVICE_INVOCATION_TRIGGER
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