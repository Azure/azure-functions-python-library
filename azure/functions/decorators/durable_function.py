#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import ORCHESTRATION_TRIGGER, \
    ACTIVITY_TRIGGER, ORCHESTRATION_CLIENT, ENTITY_TRIGGER, ENTITY_CLIENT, \
    DURABLE_CLIENT
from azure.functions.decorators.core import Trigger


class OrchestrationTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return ORCHESTRATION_TRIGGER

    def __init__(self,
                 name: str,
                 orchestration: Optional[str] = None,
                 ) -> None:
        self.orchestration = orchestration
        super().__init__(name=name, data_type=None)


class ActivityTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return ACTIVITY_TRIGGER

    def __init__(self,
                 name: str,
                 activity: Optional[str] = None,
                 ) -> None:
        self.activity = activity
        super().__init__(name=name, data_type=None)


class EntityTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return ENTITY_TRIGGER

    def __init__(self,
                 name: str,
                 entity_name: Optional[str] = None,
                 ) -> None:
        self.entity_name = entity_name
        super().__init__(name=name, data_type=None)


class EntityClient(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return ENTITY_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None,
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)


class OrchestrationClient(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return ORCHESTRATION_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)


class DurableClient(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return DURABLE_CLIENT

    def __init__(self,
                 name: str,
                 task_hub: Optional[str] = None,
                 connection_name: Optional[str] = None
                 ) -> None:
        self.task_hub = task_hub
        self.connection_name = connection_name
        super().__init__(name=name, data_type=None)
