#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from abc import ABC
from typing import Any, Callable, Optional, Union
from azure.functions.decorators.core import DataType, AuthLevel
from azure.functions.decorators.utils import parse_singular_param_to_enum
from azure.functions.decorators.function_app import DecoratorApi, FunctionRegister
from azure.functions.decorators.dapr import DaprBindingOutput, DaprBindingTrigger, DaprInvokeOutput, DaprPublishOutput, DaprSecretInput, DaprServiceInvocationTrigger, DaprStateInput, DaprStateOutput, DaprTopicTrigger

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

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-trigger-dapr

        :param arg_name: The name of the variable that represents
        :param method_name: The name of the method on a remote Dapr App. 
        If not specified, the name of the function is used as the method name.
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
        in the function.json which enables function to be triggered on Dapr input binding.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-trigger-dapr

        :param arg_name: The name of the variable that represents
        :param binding_name: The name of the Dapr trigger.
        If not specified, the name of the function is used as the trigger name.
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

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-trigger-dapr

        :param arg_name: The name of the variable that represents
        :param pub_sub_name: The pub/sub name.
        :param topic: The topic. If unspecified the function name will be used.
        :param route: The route for the trigger. If unspecified the topic name will be used.
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

class DaprBindingApi(DecoratorApi, ABC):
    
    def dapr_state_input(self,
                         arg_name: str,
                         state_store: str,
                         key: str,
                         dapr_address: Optional[str],
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) \
            -> Callable[..., Any]:
        """The dapr_state_input decorator adds
        :class:`DaprStateInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprStateInput
        in the function.json which enables function to read state from underlying state store component.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param state_store: State store containing the state.
        :param key: The name of the key.
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprStateInput(
                        name=arg_name,
                        state_store=state_store,
                        key=key,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap
    
    def dapr_secret_input(self,
                         arg_name: str,
                         secret_store_name: str,
                         key: str,
                         metadata: str,
                         dapr_address: Optional[str],
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) \
            -> Callable[..., Any]:
        """The dapr_secret_input decorator adds
        :class:`DaprSecretInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining DaprSecretInput
        in the function.json which enables function to read secret from underlying secret store component.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param secret_store_name: The name of the secret store to get the secret from.
        :param key: The key identifying the name of the secret to get.
        :param metadata: An array of metadata properties in the form "key1=value1&amp;key2=value2".
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprSecretInput(
                        name=arg_name,
                        secret_store_name=secret_store_name,
                        key=key,
                        metadata=metadata,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap
    
    def dapr_state_output(self,
                          arg_name: str,
                          state_store: str,
                          key: str,
                          dapr_address: Optional[str],
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """The dapr_state_output decorator adds
        :class:`DaprStateOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprStateOutput
        in the function.json which enables function to write to the dapr state store.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param state_store: State store containing the state for keys.
        :param key: The name of the key.
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprStateOutput(
                        name=arg_name,
                        state_store=state_store,
                        key=key,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def dapr_invoke_output(self,
                          arg_name: str,
                          app_id: str,
                          method_name: str,
                          http_verb: str,
                          dapr_address: Optional[str],
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """The dapr_invoke_output decorator adds
        :class:`DaprInvokeOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprInvokeOutput
        in the function.json which enables function to invoke another Dapr App.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param app_id: The dapr app name to invoke.
        :param method_name: The method name of the app to invoke.
        :param http_verb: The http verb of the app to invoke.
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprInvokeOutput(
                        name=arg_name,
                        app_id=app_id,
                        method_name=method_name,
                        http_verb=http_verb,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap
    
    def dapr_publish_output(self,
                          arg_name: str,
                          pub_sub_name: str,
                          topic: str,
                          dapr_address: Optional[str],
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """The dapr_publish_output decorator adds
        :class:`DaprPublishOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprPublishOutput
        in the function.json which enables function to publish topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param pub_sub_name: The pub/sub name to publish to.
        :param topic:  The name of the topic to publish to.
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprPublishOutput(
                        name=arg_name,
                        pub_sub_name=pub_sub_name,
                        topic=topic,
                        dapr_address=dapr_address,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap
    
    def dapr_binding_output(self,
                          arg_name: str,
                          binding_name: str,
                          operation: str,
                          dapr_address: Optional[str],
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) \
            -> Callable[..., Any]:
        """The dapr_binding_output decorator adds
        :class:`DaprBindingOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model.
        This is equivalent to defining DaprBindingOutput
        in the function.json which enables function to send a value to a Dapr output binding.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        TODO: need to add ref for documentation
        Ref: https://aka.ms/azure-function-binding-dapr

        :param arg_name: The name of the variable that represents DaprState
        output object in function code.
        :param arg_name: The name of the variable that represents DaprState
        input object in function code.
        :param binding_name: The configured name of the binding.
        :param operation:  The configured operation.
        :param dapr_address: Dapr address, it is optional field, by default it will be set to http://localhost:{daprHttpPort}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=DaprBindingOutput(
                        name=arg_name,
                        binding_name=binding_name,
                        operation=operation,
                        dapr_address=dapr_address,
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