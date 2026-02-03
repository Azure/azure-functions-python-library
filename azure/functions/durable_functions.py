# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
import json

from azure.functions import _durable_functions
from azure.functions.decorators.durable_functions import get_durable_package
from . import meta

import logging
_logger = logging.getLogger('azure.functions.DurableFunctions')


# ---------------- Legacy Durable Functions Converters ---------------- #
# Legacy Durable Function Orchestration Trigger
class LegacyOrchestrationTriggerConverter(meta.InConverter,
                                          meta.OutConverter,
                                          binding=None,
                                          trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.OrchestrationContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.OrchestrationContext:
        return _durable_functions.OrchestrationContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a json
        return meta.Datum(type='json', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Legacy Durable Function Entity Trigger
class LegacyEnitityTriggerConverter(meta.InConverter,
                                    meta.OutConverter,
                                    binding=None,
                                    trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.EntityContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.EntityContext:
        return _durable_functions.EntityContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a json
        return meta.Datum(type='json', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Legacy Durable Function Activity Trigger
class LegacyActivityTriggerConverter(meta.InConverter,
                                     meta.OutConverter,
                                     binding=None,
                                     trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        # Activity Trigger's arguments should accept any types
        return True

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # The activity trigger should accept any JSON serializable types
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> typing.Any:
        data_type = data.type

        # Durable functions extension always returns a string of json
        # See durable functions library's call_activity_task docs
        if data_type in ['string', 'json']:
            try:
                callback = _durable_functions._deserialize_custom_object
                result = json.loads(data.value, object_hook=callback)
            except json.JSONDecodeError:
                # String failover if the content is not json serializable
                result = data.value
            except Exception as e:
                raise ValueError(
                    'activity trigger input must be a string or a '
                    f'valid json serializable ({data.value})') from e
        else:
            raise NotImplementedError(
                f'unsupported activity trigger payload type: {data_type}')

        return result

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        try:
            callback = _durable_functions._serialize_custom_object
            result = json.dumps(obj, default=callback)
        except TypeError as e:
            raise ValueError(
                f'activity trigger output must be json serializable ({obj})') from e

        return meta.Datum(type='json', value=result)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Legacy Durable Functions Durable Client Bindings
class LegacyDurableClientConverter(meta.InConverter,
                                   meta.OutConverter,
                                   binding=None):
    @classmethod
    def has_implicit_output(cls) -> bool:
        return False

    @classmethod
    def has_trigger_support(cls) -> bool:
        return False

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes, bytearray))

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        elif obj is None:
            return meta.Datum(type=None, value=obj)
        elif isinstance(obj, dict):
            return meta.Datum(type='dict', value=obj)
        elif isinstance(obj, list):
            return meta.Datum(type='list', value=obj)
        elif isinstance(obj, bool):
            return meta.Datum(type='bool', value=obj)
        elif isinstance(obj, int):
            return meta.Datum(type='int', value=obj)
        elif isinstance(obj, float):
            return meta.Datum(type='double', value=obj)
        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        if data is None:
            return None
        data_type = data.type

        if data_type == 'string':
            result = data.value
        elif data_type == 'bytes':
            result = data.value
        elif data_type == 'json':
            result = data.value
        elif data_type is None:
            result = None
        else:
            raise ValueError(
                'unexpected type of data received for the "generic" binding ',
                repr(data_type)
            )

        return result


# ---------------- Durable Task Durable Functions Converters ---------------- #
# Durable Function Orchestration Trigger
class OrchestrationTriggerConverter(meta.InConverter,
                                    meta.OutConverter,
                                    binding=None,
                                    trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.OrchestrationContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.OrchestrationContext:
        return _durable_functions.OrchestrationContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a string
        return meta.Datum(type='string', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Durable Function Entity Trigger
class EnitityTriggerConverter(meta.InConverter,
                              meta.OutConverter,
                              binding=None,
                              trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        return issubclass(pytype, _durable_functions.EntityContext)

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # Implicit output should accept any return type
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> _durable_functions.EntityContext:
        return _durable_functions.EntityContext(data.value)

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        # Durable function context should be a string
        return meta.Datum(type='string', value=obj)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Durable Function Activity Trigger
class ActivityTriggerConverter(meta.InConverter,
                               meta.OutConverter,
                               binding=None,
                               trigger=True):
    @classmethod
    def check_input_type_annotation(cls, pytype):
        # Activity Trigger's arguments should accept any types
        return True

    @classmethod
    def check_output_type_annotation(cls, pytype):
        # The activity trigger should accept any JSON serializable types
        return True

    @classmethod
    def decode(cls,
               data: meta.Datum, *,
               trigger_metadata) -> typing.Any:
        data_type = data.type

        # Durable functions extension always returns a string of json
        # See durable functions library's call_activity_task docs
        if data_type in ['string', 'json']:
            try:
                callback = _durable_functions._deserialize_custom_object
                result = json.loads(data.value, object_hook=callback)
            except json.JSONDecodeError:
                # String failover if the content is not json serializable
                result = data.value
            except Exception as e:
                raise ValueError(
                    'activity trigger input must be a string or a '
                    f'valid json serializable ({data.value})') from e
        else:
            raise NotImplementedError(
                f'unsupported activity trigger payload type: {data_type}')

        return result

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        try:
            callback = _durable_functions._serialize_custom_object
            result = json.dumps(obj, default=callback)
        except TypeError as e:
            raise ValueError(
                f'activity trigger output must be json serializable ({obj})') from e

        return meta.Datum(type='json', value=result)

    @classmethod
    def has_implicit_output(cls) -> bool:
        return True


# Durable Functions Durable Client Bindings
class DurableClientConverter(meta.InConverter,
                             meta.OutConverter,
                             binding=None):
    @classmethod
    def has_implicit_output(cls) -> bool:
        return False

    @classmethod
    def has_trigger_support(cls) -> bool:
        return False

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        import azure.durable_functions as adf
        return issubclass(pytype, (str, bytes, adf.DurableFunctionsClient))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (str, bytes, bytearray))

    @classmethod
    def encode(cls, obj: typing.Any, *,
               expected_type: typing.Optional[type]) -> meta.Datum:
        if isinstance(obj, str):
            return meta.Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return meta.Datum(type='bytes', value=bytes(obj))
        elif obj is None:
            return meta.Datum(type=None, value=obj)
        elif isinstance(obj, dict):
            return meta.Datum(type='dict', value=obj)
        elif isinstance(obj, list):
            return meta.Datum(type='list', value=obj)
        elif isinstance(obj, bool):
            return meta.Datum(type='bool', value=obj)
        elif isinstance(obj, int):
            return meta.Datum(type='int', value=obj)
        elif isinstance(obj, float):
            return meta.Datum(type='double', value=obj)
        else:
            raise NotImplementedError

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        import azure.durable_functions as adf
        return adf.DurableFunctionsClient(data.value)


def register_durable_converters():
    """
    Registers the appropriate Durable Functions converters based on the
    installed Durable Functions package.
    """
    _logger.info("Registering Durable Functions converters based on ")
    pkg = get_durable_package()
    if pkg is None:
        # Durable library not installed → do nothing
        return

    _logger.info("Durable Functions package loaded: %s", pkg.__name__)
    _logger.info("Current bindings before registration: %s", meta._ConverterMeta._bindings)
    # Clear existing bindings if they exist
    meta._ConverterMeta._bindings.pop("orchestrationTrigger", None)
    meta._ConverterMeta._bindings.pop("entityTrigger", None)
    meta._ConverterMeta._bindings.pop("activityTrigger", None)
    meta._ConverterMeta._bindings.pop("durableClient", None)

    if not hasattr(pkg, 'version'):
        _logger.info("Registering Legacy Durable Functions converters.")
        meta._ConverterMeta._bindings["orchestrationTrigger"] = LegacyOrchestrationTriggerConverter
        meta._ConverterMeta._bindings["entityTrigger"] = LegacyEnitityTriggerConverter
        meta._ConverterMeta._bindings["activityTrigger"] = LegacyActivityTriggerConverter
        meta._ConverterMeta._bindings["durableClient"] = LegacyDurableClientConverter
    elif hasattr(pkg, 'version') and pkg.version.startswith("2."):
        _logger.info("Registering Durable Task Durable Functions converters.")
        meta._ConverterMeta._bindings["orchestrationTrigger"] = OrchestrationTriggerConverter
        meta._ConverterMeta._bindings["entityTrigger"] = EnitityTriggerConverter
        meta._ConverterMeta._bindings["activityTrigger"] = ActivityTriggerConverter
        meta._ConverterMeta._bindings["durableClient"] = DurableClientConverter

    _logger.info("Durable Functions converters registered.")
    _logger.info("Current bindings after registration: %s", meta._ConverterMeta._bindings)
