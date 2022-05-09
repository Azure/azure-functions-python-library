#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
from typing import Callable, Dict, List, Optional, Union, Iterable

from azure.functions.decorators.blob import BlobTrigger, BlobInput, BlobOutput
from azure.functions.decorators.core import Binding, Trigger, DataType, \
    AuthLevel, SCRIPT_FILE_NAME, Cardinality, AccessRights
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput
from azure.functions.decorators.eventhub import EventHubTrigger, EventHubOutput
from azure.functions.decorators.http import HttpTrigger, HttpOutput, \
    HttpMethod
from azure.functions.decorators.eventgrid import EventGridTrigger, \
    EventGridOutput
from azure.functions.decorators.queue import QueueTrigger, QueueOutput
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput
from azure.functions.decorators.timer import TimerTrigger
from azure.functions.decorators.utils import parse_singular_param_to_enum, \
    parse_iterable_param_to_enums, StringifyEnumJsonEncoder
from azure.functions.http import HttpRequest
from .constants import HTTP_TRIGGER
from .generic import GenericInputBinding, GenericTrigger, GenericOutputBinding
from .._http_asgi import AsgiMiddleware
from .._http_wsgi import WsgiMiddleware, Context


class Function(object):
    """The function object represents a function in Function App. It
    encapsulates function metadata and callable and used in the worker
    function indexing model. Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self, func: Callable, script_file: str):
        """Constructor of :class:`FunctionBuilder` object.

        :param func: User defined python function instance.
        :param script_file: File name indexed by worker to find function.
        """
        self._name: str = func.__name__
        self._func = func
        self._trigger: Optional[Trigger] = None
        self._bindings: List[Binding] = []
        self.function_script_file = script_file

    def add_binding(self, binding: Binding) -> None:
        """Add a binding instance to the function.

        :param binding: The binding object to add.
        """
        self._bindings.append(binding)

    def add_trigger(self, trigger: Trigger) -> None:
        """Add a trigger instance to the function.

        :param trigger: The trigger object to add.
        :raises ValueError: Raises trigger already exists error if a trigger is
             being added to a function which has trigger attached.
        """

        if self._trigger:
            raise ValueError("A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one"
                             " trigger. Existing registered trigger "
                             f"is {self._trigger.get_dict_repr()} and New "
                             f"trigger "
                             f"being added is {trigger.get_dict_repr()}")

        self._trigger = trigger

        #  We still add the trigger info to the bindings to ensure that
        #  function.json is complete
        self._bindings.append(trigger)

    def set_function_name(self, function_name: Optional[str] = None) -> None:
        """Set or update the name for the function if :param:`function_name`
         is not None. If not set, function name will default to python
        function name.
        :param function_name: Name the function set to.
        """
        if function_name:
            self._name = function_name

    def get_trigger(self) -> Optional[Trigger]:
        """Get attached trigger instance of the function.

        :return: Trigger instance or None.
        """
        return self._trigger

    def get_bindings(self) -> List[Binding]:
        """Get all the bindings attached to the function.

        :return: Bindings attached to the function.
        """
        return self._bindings

    def get_raw_bindings(self) -> List[str]:
        return [json.dumps(i, cls=StringifyEnumJsonEncoder) for i in
                self.get_bindings_dict()["bindings"]]

    def get_bindings_dict(self) -> Dict:
        """Get dictionary representation of the bindings of the function.

        :return: Dictionary representation of the bindings.
        """
        return {"bindings": [b.get_dict_repr() for b in self._bindings]}

    def get_dict_repr(self) -> Dict:
        """Get the dictionary representation of the function.

        :return: The dictionary representation of the function.
        """
        stub_f_json = {
            "scriptFile": self.function_script_file
        }
        stub_f_json.update(self.get_bindings_dict())  # NoQA
        return stub_f_json

    def get_user_function(self) -> Callable:
        """Get the python function customer defined.

        :return: The python function customer defined.
        """
        return self._func

    def get_function_name(self) -> str:
        """Get the function name.

        :return: Function name.
        """
        return self._name

    def get_function_json(self) -> str:
        """Get the json stringified form of function.

        :return: The json stringified form of function.
        """
        return json.dumps(self.get_dict_repr(), cls=StringifyEnumJsonEncoder)

    def __str__(self):
        return self.get_function_json()


class FunctionBuilder(object):
    def __init__(self, func, function_script_file):
        self._function = Function(func, function_script_file)

    def __call__(self, *args, **kwargs):
        pass

    def configure_function_name(self, function_name: str) -> 'FunctionBuilder':
        self._function.set_function_name(function_name)

        return self

    def add_trigger(self, trigger: Trigger) -> 'FunctionBuilder':
        self._function.add_trigger(trigger=trigger)
        return self

    def add_binding(self, binding: Binding) -> 'FunctionBuilder':
        self._function.add_binding(binding=binding)
        return self

    def _validate_function(self) -> None:
        function_name = self._function.get_function_name()
        trigger = self._function.get_trigger()
        if trigger is None:
            raise ValueError(
                f"Function {function_name} does not have a trigger. A valid "
                f"function must have one and only one trigger registered.")

        bindings = self._function.get_bindings()
        if trigger not in bindings:
            raise ValueError(
                f"Function {function_name} trigger {trigger} not present"
                f" in bindings {bindings}")

        # Set route to function name if unspecified in the http trigger
        if Trigger.is_supported_trigger_type(trigger, HttpTrigger) \
                and getattr(trigger, 'route', None) is None:
            setattr(trigger, 'route', function_name)

    def build(self) -> Function:
        self._validate_function()
        return self._function


class FunctionApp:
    """FunctionApp object used by worker function indexing model captures
    user defined functions and metadata.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION,
                 **kwargs):
        """Constructor of :class:`FunctionApp` object.
        To integrate your asgi or wsgi application into python function,
        specify either of below variables as a keyword argument:
        `asgi_app` - the actual asgi application to integrate into python
        function.
        `wsgi_app` - the actual wsgi application to integrate into python
        function.

        :param http_auth_level: defaults to AuthLevel.FUNCTION, takes str or
        AuthLevel.
        :param kwargs: Extra arguments passed to :func:`__init__`.
        """
        self._function_builders: List[FunctionBuilder] = []
        self._app_script_file: str = SCRIPT_FILE_NAME
        self._auth_level = AuthLevel[http_auth_level] \
            if isinstance(http_auth_level, str) else http_auth_level

        wsgi_app = kwargs.get("wsgi_app", None)
        asgi_app = kwargs.get("asgi_app", None)

        if wsgi_app is not None:
            self._add_http_app(WsgiMiddleware(wsgi_app))

        if asgi_app is not None:
            self._add_http_app(AsgiMiddleware(asgi_app))

    @property
    def app_script_file(self) -> str:
        """Name of function app script file in which all the functions
         are defined. \n
         Script file defined here is for placeholder purpose, please refer to
         worker defined script file path as the single point of truth.

        :return: Script file name.
        """
        return self._app_script_file

    @property
    def auth_level(self) -> AuthLevel:
        """Authorization level of the function app. Will be applied to the http
         trigger functions which does not have authorization level specified.

        :return: Authorization level of the function app.
        """

        return self._auth_level

    def get_functions(self) -> List[Function]:
        """Get the function objects in the function app.

        :return: List of functions in the function app.
        """
        return [function_builder.build() for function_builder
                in self._function_builders]

    def _validate_type(self, func: Union[Callable, FunctionBuilder]) \
            -> FunctionBuilder:
        """Validate the type of the function object and return the created
        :class:`FunctionBuilder` object.


        :param func: Function object passed to
         :meth:`_configure_function_builder`
        :raises ValueError: Raise error when func param is neither
         :class:`Callable` nor :class:`FunctionBuilder`.
        :return: :class:`FunctionBuilder` object.
        """
        if isinstance(func, FunctionBuilder):
            fb = self._function_builders.pop()
        elif callable(func):
            fb = FunctionBuilder(func, self._app_script_file)
        else:
            raise ValueError(
                "Unsupported type for function app decorator found.")
        return fb

    def _configure_function_builder(self, wrap) -> Callable:
        """Decorator function on user defined function to create and return
         :class:`FunctionBuilder` object from :class:`Callable` func.
        """

        def decorator(func):
            fb = self._validate_type(func)
            self._function_builders.append(fb)
            return wrap(fb)

        return decorator

    def function_name(self, name: str) -> Callable:
        """Set name of the :class:`Function` object.

        :param name: Name of the function.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.configure_function_name(name)
                return fb

            return decorator()

        return wrap

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware]) -> None:
        """Add a Wsgi or Asgi app integrated http function.

        :param http_middleware: :class:`AsgiMiddleware` or
        :class:`WsgiMiddleware` instance.

        :return: None
        """

        @self.route(methods=(method for method in HttpMethod),
                    auth_level=self.auth_level,
                    route="/{*route}")
        def http_app_func(req: HttpRequest, context: Context):
            return http_middleware.handle(req, context)

    def route(self,
              route: Optional[str] = None,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              methods: Optional[
                  Union[Iterable[str], Iterable[HttpMethod]]] = None,
              auth_level: Optional[Union[AuthLevel, str]] = None,
              trigger_extra_fields: Dict = {},
              binding_extra_fields: Dict = {}
              ) -> Callable:
        """The route decorator adds :class:`HttpTrigger` and
        :class:`HttpOutput` binding to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining HttpTrigger
        and HttpOutput binding in the function.json which enables your
        function be triggered when http requests hit the specified route.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-http

        :param route: Route for the http endpoint, if None, it will be set
        to function name if present or user defined python function name.
        :param trigger_arg_name: Argument name for :class:`HttpRequest`,
        defaults to 'req'.
        :param binding_arg_name: Argument name for :class:`HttpResponse`,
        defaults to '$return'.
        :param methods: A tuple of the HTTP methods to which the function
        responds.
        :param auth_level: Determines what keys, if any, need to be present
        on the request in order to invoke the function.
        :return: Decorator function.
        :param trigger_extra_fields: Additional fields to include in trigger
        json. For example,
        >>> data_type='STRING' # 'dataType': 'STRING' in trigger json
        :param binding_extra_fields: Additional fields to include in binding
        json. For example,
        >>> data_type='STRING' # 'dataType': 'STRING' in binding json
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                nonlocal auth_level
                if auth_level is None:
                    auth_level = self.auth_level

                fb.add_trigger(trigger=HttpTrigger(
                    name=trigger_arg_name,
                    methods=parse_iterable_param_to_enums(methods, HttpMethod),
                    auth_level=parse_singular_param_to_enum(auth_level,
                                                            AuthLevel),
                    route=route, **trigger_extra_fields))
                fb.add_binding(binding=HttpOutput(
                    name=binding_arg_name, **binding_extra_fields))
                return fb

            return decorator()

        return wrap

    def schedule(self,
                 arg_name: str,
                 schedule: str,
                 run_on_startup: Optional[bool] = None,
                 use_monitor: Optional[bool] = None,
                 data_type: Optional[Union[DataType, str]] = None,
                 **kwargs) -> Callable:
        """The schedule decorator adds :class:`TimerTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TimerTrigger
        in the function.json which enables your function be triggered on the
        specified schedule.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-timer

        :param arg_name: The name of the variable that represents the
        :class:`TimerRequest` object in function code.
        :param schedule: A string representing a CRON expression that will
        be used to schedule a function to run.
        :param run_on_startup: If true, the function is invoked when the
        runtime starts.
        :param use_monitor: Set to true or false to indicate whether the
        schedule should be monitored.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=TimerTrigger(
                        name=arg_name,
                        schedule=schedule,
                        run_on_startup=run_on_startup,
                        use_monitor=use_monitor,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def service_bus_queue_trigger(
            self,
            arg_name: str,
            connection: str,
            queue_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None,
            **kwargs) -> Callable:
        """The on_service_bus_queue_change decorator adds
        :class:`ServiceBusQueueTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueTrigger
        in the function.json which enables your function be triggered when
        new message(s) are sent to the service bus queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription.
        :param cardinality: Set to many in order to enable batching.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusQueueTrigger(
                        name=arg_name,
                        connection=connection,
                        queue_name=queue_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_service_bus_queue(self,
                                arg_name: str,
                                connection: str,
                                queue_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                access_rights: Optional[Union[
                                    AccessRights, str]] = None,
                                **kwargs) -> \
            Callable:
        """The write_service_bus_queue decorator adds
        :class:`ServiceBusQueueOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueOutput
        in the function.json which enables function to write message(s) to
        the service bus queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus queue output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusQueueOutput(
                        name=arg_name,
                        connection=connection,
                        queue_name=queue_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights, AccessRights),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def service_bus_topic_trigger(
            self,
            arg_name: str,
            connection: str,
            topic_name: str,
            subscription_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None,
            **kwargs) -> Callable:
        """The on_service_bus_topic_change decorator adds
        :class:`ServiceBusTopicTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the service bus topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param access_rights: Access rights for the connection string.
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription.
        :param cardinality: Set to many in order to enable batching.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusTopicTrigger(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_service_bus_topic(self,
                                arg_name: str,
                                connection: str,
                                topic_name: str,
                                subscription_name: Optional[str] = None,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                access_rights: Optional[Union[
                                    AccessRights, str]] = None,
                                **kwargs) -> \
            Callable:
        """The write_service_bus_topic decorator adds
        :class:`ServiceBusTopicOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicOutput
        in the function.json which enables function to write message(s) to
        the service bus topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus topic output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusTopicOutput(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        access_rights=parse_singular_param_to_enum(
                            access_rights,
                            AccessRights),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def queue_trigger(self,
                      arg_name: str,
                      queue_name: str,
                      connection: str,
                      data_type: Optional[DataType] = None,
                      **kwargs) -> Callable:
        """The queue_trigger decorator adds :class:`QueueTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the storage queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents the
        :class:`QueueMessage` object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=QueueTrigger(
                        name=arg_name,
                        queue_name=queue_name,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_queue(self,
                    arg_name: str,
                    queue_name: str,
                    connection: str,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable:
        """The write_queue decorator adds :class:`QueueOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueOutput
        in the function.json which enables function to write message(s) to
        the storage queue.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents storage
        queue output object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=QueueOutput(name=arg_name,
                                        queue_name=queue_name,
                                        connection=connection,
                                        data_type=parse_singular_param_to_enum(
                                            data_type, DataType),
                                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_hub_message_trigger(self,
                                  arg_name: str,
                                  connection: str,
                                  event_hub_name: str,
                                  data_type: Optional[
                                      Union[DataType, str]] = None,
                                  cardinality: Optional[
                                      Union[Cardinality, str]] = None,
                                  consumer_group: Optional[
                                      str] = None,
                                  **kwargs) -> Callable:
        """The event_hub_message_trigger decorator adds
        :class:`EventHubTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the event hub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :class:`EventHubEvent` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hubs.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param cardinality: Set to many in order to enable batching.
        :param consumer_group: An optional property that sets the consumer
        group used to subscribe to events in the hub.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EventHubTrigger(
                        name=arg_name,
                        connection=connection,
                        event_hub_name=event_hub_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        cardinality=parse_singular_param_to_enum(cardinality,
                                                                 Cardinality),
                        consumer_group=consumer_group,
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_event_hub_message(self,
                                arg_name: str,
                                connection: str,
                                event_hub_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None,
                                **kwargs) -> \
            Callable:
        """The write_event_hub_message decorator adds
        :class:`EventHubOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubOutput
        in the function.json which enables function to write message(s) to
        the event hub.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents event hub
        output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hub.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EventHubOutput(
                        name=arg_name,
                        connection=connection,
                        event_hub_name=event_hub_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def cosmos_db_trigger(self,
                          arg_name: str,
                          database_name: str,
                          collection_name: str,
                          connection_string_setting: str,
                          lease_collection_name: Optional[str] = None,
                          lease_connection_string_setting: Optional[
                              str] = None,
                          lease_database_name: Optional[str] = None,
                          create_lease_collection_if_not_exists: Optional[
                              bool] = None,
                          leases_collection_throughput: Optional[int] = None,
                          lease_collection_prefix: Optional[str] = None,
                          checkpoint_interval: Optional[int] = None,
                          checkpoint_document_count: Optional[int] = None,
                          feed_poll_delay: Optional[int] = None,
                          lease_renew_interval: Optional[int] = None,
                          lease_acquire_interval: Optional[int] = None,
                          lease_expiration_interval: Optional[int] = None,
                          max_items_per_invocation: Optional[int] = None,
                          start_from_beginning: Optional[bool] = None,
                          preferred_locations: Optional[str] = None,
                          data_type: Optional[
                              Union[DataType, str]] = None,
                          **kwargs) -> \
            Callable:
        """The cosmos_db_trigger decorator adds :class:`CosmosDBTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBTrigger
        in the function.json which enables function to be triggered when
        CosmosDB data is changed.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` object in function code.
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored.
        :param collection_name: The name of the collection being monitored.
        :param connection_string_setting: The name of an app setting or
        setting collection that specifies how to connect to the Azure Cosmos
        DB account being monitored.
        :param lease_collection_name: The name of the collection used to
        store leases.
        :param lease_connection_string_setting: The name of an app setting
        or setting collection that specifies how to connect to the Azure
        Cosmos DB account that holds the lease collection.
        :param lease_database_name: The name of the database that holds the
        collection used to store leases.
        :param create_lease_collection_if_not_exists: When set to true,
        the leases collection is automatically created when it doesn't
        already exist.
        :param leases_collection_throughput: Defines the number of Request
        Units to assign when the leases collection is created.
        :param lease_collection_prefix: When set, the value is added as a
        prefix to the leases created in the Lease collection for this
        Function.
        :param checkpoint_interval: When set, it defines, in milliseconds,
        the interval between lease checkpoints. Default is always after a
        Function call.
        :param checkpoint_document_count: Customizes the amount of documents
        between lease checkpoints. Default is always after a Function call.
        :param feed_poll_delay: The time (in milliseconds) for the delay
        between polling a partition for new changes on the feed, after all
        current changes are drained.
        :param lease_renew_interval: When set, it defines, in milliseconds,
        the renew interval for all leases for partitions currently held by
        an instance.
        :param lease_acquire_interval: When set, it defines,
        in milliseconds, the interval to kick off a task to compute if
        partitions are distributed evenly among known host instances.
        :param lease_expiration_interval: When set, it defines,
        in milliseconds, the interval for which the lease is taken on a
        lease representing a partition.
        :param max_items_per_invocation: When set, this property sets the
        maximum number of items received per Function call.
        :param start_from_beginning: This option tells the Trigger to read
        changes from the beginning of the collection's change history
        instead of starting at the current time.
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """
        trigger = CosmosDBTrigger(
            name=arg_name,
            database_name=database_name,
            collection_name=collection_name,
            connection_string_setting=connection_string_setting,
            lease_collection_name=lease_collection_name,
            lease_connection_string_setting=lease_connection_string_setting,
            lease_database_name=lease_database_name,
            create_lease_collection_if_not_exists  # NoQA
            =create_lease_collection_if_not_exists,
            leases_collection_throughput=leases_collection_throughput,
            lease_collection_prefix=lease_collection_prefix,
            checkpoint_interval=checkpoint_interval,
            checkpoint_document_count=checkpoint_document_count,
            feed_poll_delay=feed_poll_delay,
            lease_renew_interval=lease_renew_interval,
            lease_acquire_interval=lease_acquire_interval,
            lease_expiration_interval=lease_expiration_interval,
            max_items_per_invocation=max_items_per_invocation,
            start_from_beginning=start_from_beginning,
            preferred_locations=preferred_locations,
            data_type=parse_singular_param_to_enum(data_type, DataType),
            **kwargs)

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(trigger=trigger)
                return fb

            return decorator()

        return wrap

    def write_cosmos_db_documents(self,
                                  arg_name: str,
                                  database_name: str,
                                  collection_name: str,
                                  connection_string_setting: str,
                                  create_if_not_exists: Optional[bool] = None,
                                  partition_key: Optional[str] = None,
                                  collection_throughput: Optional[int] = None,
                                  use_multiple_write_locations: Optional[
                                      bool] = None,
                                  preferred_locations: Optional[str] = None,
                                  data_type: Optional[
                                      Union[DataType, str]] = None,
                                  **kwargs) \
            -> Callable:
        """The write_cosmos_db_documents decorator adds
        :class:`CosmosDBOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBOutput
        in the function.json which enables function to write to the CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents CosmosDB
        output object in function code.
        :param database_name: The name of the Azure Cosmos DB database with
        the collection being monitored.
        :param collection_name: The name of the collection being monitored.
        :param connection_string_setting: The name of an app setting or
        setting collection that specifies how to connect to the Azure Cosmos
        DB account being monitored.
        :param create_if_not_exists: A boolean value to indicate whether the
        collection is created when it doesn't exist.
        :param partition_key: When CreateIfNotExists is true, it defines the
        partition key path for the created collection.
        :param collection_throughput: When CreateIfNotExists is true,
        it defines the throughput of the created collection.
        :param use_multiple_write_locations: When set to true along with
        PreferredLocations, it can leverage multi-region writes in the Azure
        Cosmos DB service.
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBOutput(
                        name=arg_name,
                        database_name=database_name,
                        collection_name=collection_name,
                        connection_string_setting=connection_string_setting,
                        create_if_not_exists=create_if_not_exists,
                        partition_key=partition_key,
                        collection_throughput=collection_throughput,
                        use_multiple_write_locations  # NoQA
                        =use_multiple_write_locations,
                        preferred_locations=preferred_locations,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def read_cosmos_db_documents(self,
                                 arg_name: str,
                                 database_name: str,
                                 collection_name: str,
                                 connection_string_setting: str,
                                 id: Optional[str] = None,
                                 sql_query: Optional[str] = None,
                                 partition_key: Optional[str] = None,
                                 data_type: Optional[
                                     Union[DataType, str]] = None,
                                 **kwargs) \
            -> Callable:
        """The read_cosmos_db_documents decorator adds
        :class:`CosmosDBInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBInput
        in the function.json which enables function to read from CosmosDB.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` input object in function code.
        :param database_name: The database containing the document.
        :param collection_name: The name of the collection that contains the
        document.
        :param connection_string_setting: The name of the app setting
        containing your Azure Cosmos DB connection string.
        :param id: The ID of the document to retrieve.
        :param sql_query: An Azure Cosmos DB SQL query used for retrieving
        multiple documents.
        :param partition_key: Specifies the partition key value for the
        lookup.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBInput(
                        name=arg_name,
                        database_name=database_name,
                        collection_name=collection_name,
                        connection_string_setting=connection_string_setting,
                        id=id,
                        sql_query=sql_query,
                        partition_key=partition_key,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def blob_trigger(self,
                     arg_name: str,
                     path: str,
                     connection: str,
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable:
        """
        The blob_change_trigger decorator adds :class:`BlobTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the
        :class:`InputStream` object in function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=BlobTrigger(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def read_blob(self,
                  arg_name: str,
                  path: str,
                  connection: str,
                  data_type: Optional[DataType] = None,
                  **kwargs) -> Callable:

        """
        The read_blob decorator adds :class:`BlobInput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobInput
        in the function.json which enables function to write message(s) to
        the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in
         function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=BlobInput(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_blob(self,
                   arg_name: str,
                   path: str,
                   connection: str,
                   data_type: Optional[DataType] = None,
                   **kwargs) -> Callable:

        """
        The write_blob decorator adds :class:`BlobOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining BlobOutput
        in the function.json which enables function to write message(s) to
        the storage blobs.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-storage-blob

        :param arg_name: The name of the variable that represents the blob in
         function code.
        :param path: The path to the blob.
        :param connection: The name of an app setting or setting collection
         that specifies how to connect to Azure Blobs.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=BlobOutput(
                        name=arg_name,
                        path=path,
                        connection=connection,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_input_binding(self,
                              arg_name: str,
                              type: str,
                              data_type: Optional[Union[DataType, str]] = None,
                              **kwargs
                              ) -> Callable:
        """
        The generic_input_binding decorator adds :class:`GenericInputBinding`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic input binding in the
        function.json which enables function to read data from a
        custom defined input source.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of input parameter in the function code.
        :param type: The type of binding.
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
                    binding=GenericInputBinding(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_output_binding(self,
                               arg_name: str,
                               type: str,
                               data_type: Optional[
                                   Union[DataType, str]] = None,
                               **kwargs
                               ) -> Callable:
        """
        The generic_output_binding decorator adds :class:`GenericOutputBinding`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic output binding in the
        function.json which enables function to write data from a
        custom defined output source.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of output parameter in the function code.
        :param type: The type of binding.
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
                    binding=GenericOutputBinding(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def generic_trigger(self,
                        arg_name: str,
                        type: str,
                        data_type: Optional[Union[DataType, str]] = None,
                        **kwargs
                        ) -> Callable:
        """
        The generic_trigger decorator adds :class:`GenericTrigger`
        to the :class:`FunctionBuilder` object for building :class:`Function`
        object used in worker function indexing model.
        This is equivalent to defining a generic trigger in the
        function.json which triggers function to execute when generic trigger
        events are received by host.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/azure-function-binding-custom

        :param arg_name: The name of trigger parameter in the function code.
        :param type: The type of binding.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                nonlocal kwargs
                if type == HTTP_TRIGGER:
                    if kwargs.get('auth_level', None) is None:
                        kwargs['auth_level'] = self.auth_level
                    if 'route' not in kwargs:
                        kwargs['route'] = None
                fb.add_trigger(
                    trigger=GenericTrigger(
                        name=arg_name,
                        type=type,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def event_grid_trigger(self,
                           arg_name: str,
                           data_type: Optional[
                               Union[DataType, str]] = None,
                           **kwargs) -> Callable:
        """
        The event_grid_trigger decorator adds
        :class:`EventGridTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining event grid trigger
        in the function.json which enables function to be triggered to
        respond to an event sent to an event grid topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: the variable name used in function code for the
         parameter that receives the event data.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EventGridTrigger(
                        name=arg_name,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap

    def write_event_grid(self,
                         arg_name: str,
                         topic_endpoint_uri: str,
                         topic_key_setting: str,
                         data_type: Optional[
                             Union[DataType, str]] = None,
                         **kwargs) -> Callable:
        """
        The write_event_grid decorator adds
        :class:`EventGridOutput`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining output binding
        in the function.json which enables function to
        write events to a custom topic.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/eventgridtrigger

        :param arg_name: The variable name used in function code that
        represents the event.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param topic_endpoint_uri: 	The name of an app setting that
        contains the URI for the custom topic.
        :param topic_key_setting: The name of an app setting that
        contains an access key for the custom topic.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EventGridOutput(
                        name=arg_name,
                        topic_endpoint_uri=topic_endpoint_uri,
                        topic_key_setting=topic_key_setting,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType),
                        **kwargs))
                return fb

            return decorator()

        return wrap
