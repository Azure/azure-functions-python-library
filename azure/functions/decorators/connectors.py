#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.core import Trigger, \
    DataType


class ConnectorTrigger(Trigger):

    @staticmethod
    def get_binding_name():
        from azure.functions.decorators.constants import CONNECTOR_TRIGGER
        return CONNECTOR_TRIGGER

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 **kwargs):
        from azure.functions.decorators.constants import CONNECTOR_TRIGGER
        super().__init__(name=name, data_type=data_type, type=CONNECTOR_TRIGGER)
