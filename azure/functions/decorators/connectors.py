#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional, Union

from azure.functions.decorators.core import Trigger, \
    DataType, Cardinality, DeliveryMode
from azure.functions.decorators.utils import parse_singular_param_to_enum


class ConnectorTrigger(Trigger):

    @staticmethod
    def get_binding_name():
        from azure.functions.decorators.constants import CONNECTOR_TRIGGER
        return CONNECTOR_TRIGGER

    def __init__(self,
                 name: str,
                 data_type: Optional[DataType] = None,
                 delivery_mode: Optional[Union[DeliveryMode, str]] = None,
                 connection: Optional[str] = None,
                 trigger_config_name: Optional[str] = None,
                 cardinality: Optional[Union[Cardinality, str]] = None,
                 max_batch_size: Optional[int] = None,
                 max_concurrent_calls: Optional[int] = None,
                 target_pending_event_threshold: Optional[int] = None,
                 **kwargs):
        from azure.functions.decorators.constants import CONNECTOR_TRIGGER
        delivery_mode = parse_singular_param_to_enum(delivery_mode, DeliveryMode)
        cardinality = parse_singular_param_to_enum(cardinality, Cardinality)
        if delivery_mode == DeliveryMode.POLL:
            required_params = {
                "connection": connection,
                "trigger_config_name": trigger_config_name,
            }
            missing_params = [
                key for key, value in required_params.items() if value is None
            ]
            if missing_params:
                raise ValueError(
                    "The following parameters are required for Poll delivery "
                    "mode: %s" % ', '.join(missing_params))

        self.delivery_mode = delivery_mode
        self.connection = connection
        self.trigger_config_name = trigger_config_name
        self.cardinality = cardinality
        self.max_batch_size = max_batch_size
        self.max_concurrent_calls = max_concurrent_calls
        self.target_pending_event_threshold = target_pending_event_threshold
        super().__init__(name=name, data_type=data_type, type=CONNECTOR_TRIGGER)
