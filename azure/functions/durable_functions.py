from typing import Any
from azure.functions import _durable_functions

from . import meta


# Durable Function Orchestration Trigger
class OrchestrationTriggerConverter(meta.InConverter,
                                    binding='orchestrationTrigger',
                                    trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.OrchestrationContext)

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.OrchestrationContext:
        return _durable_functions.OrchestrationContext(data.value)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Durable Function Activity Trigger
class ActivityTriggerConverter(meta.InConverter,
                               binding='activityTrigger',
                               trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        # Activity Trigger's arguments should accept any types
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> Any:
        if getattr(data, 'value', None) is not None:
            return data.value

        return data

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True
