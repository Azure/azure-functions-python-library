#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from abc import ABC
from typing import Any, Callable, Optional, Union
from azure.functions.decorators.core import DataType, AuthLevel
from azure.functions.decorators.utils import parse_singular_param_to_enum
from azure.functions.decorators.function_app import DecoratorApi, FunctionRegister
from azure.functions.decorators.dapr import DaprBindingTrigger, DaprServiceInvocationTrigger, DaprTopicTrigger

class DaprTriggerApi(DecoratorApi, ABC):

    def dapr_service_invocation_trigger(self,
                                arg_name: str,
                                method_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs: Any) -> Callable[..., Any]:
        """The dapr_service_invocation_trigger decorator adds
        :class:`DaprServiceInvocationTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprServiceInvocationTrigger
        in the function.json which enables function to be triggered when new
        service invocation occurs through Dapr.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :param method_name: The name of the service method to be invoked by Dapr.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprServiceInvocationTrigger(
                        name=arg_name,
                        method_name=method_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                                DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_binding_trigger(self,
                                arg_name: str,
                                binding_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs: Any) -> Callable[..., Any]:
        """The dapr_binding_trigger decorator adds
        :class:`DaprBindingTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprBindingTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the event hub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :param binding_name: The name of the binding to be invoked by Dapr.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprBindingTrigger(
                        name=arg_name,
                        binding_name=binding_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                                DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_topic_trigger(self,
                                arg_name: str,
                                pub_sub_name: str,
                                topic: str,
                                route: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs: Any) -> Callable[..., Any]:
        """The dapr_topic_trigger decorator adds
        :class:`DaprTopicTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprTopicTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the Dapr pubsub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :param pub_sub_name: The name of the pubsub.
        :param topic: The name of the topic.
        :param route: The name of the route.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=DaprTopicTrigger(
                        name=arg_name,
                        pub_sub_name=pub_sub_name,
                        topic=topic,
                        route=route,
                        data_type=parse_singular_param_to_enum(data_type,
                                                                DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

class DaprFunctionApp(FunctionRegister, DaprTriggerApi):

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`DaprFunctionApp` object.

        :param http_auth_level: Determines what keys, if any, need to be
        present
        on the request in order to invoke the function.
        """
        super().__init__(auth_level=http_auth_level)