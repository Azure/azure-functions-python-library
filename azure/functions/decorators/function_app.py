#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
from typing import Callable, Dict, List, Optional, Union, Iterable

from azure.functions.decorators import Cardinality, AccessRights
from azure.functions.decorators.core import Binding, Trigger, DataType, \
    AuthLevel, SCRIPT_FILE_NAME
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput
from azure.functions.decorators.eventhub import EventHubTrigger, EventHubOutput
from azure.functions.decorators.http import HttpTrigger, HttpOutput, HttpMethod
from azure.functions.decorators.queue import QueueTrigger, QueueOutput
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput
from azure.functions.decorators.timer import TimerTrigger
from azure.functions.decorators.utils import parse_singular_param_to_enum, \
    parse_iterable_param_to_enum, CustomJsonEncoder


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
                             f"is {self._trigger} and New "
                             f"trigger "
                             f"being added is {trigger}")

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
        return [json.dumps(i, cls=CustomJsonEncoder) for i in
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
        return json.dumps(self.get_dict_repr(), cls=CustomJsonEncoder)

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
                f"Function {function_name} does not have a trigger")

        bindings = self._function.get_bindings()
        if trigger not in bindings:
            raise ValueError(
                f"Function {function_name} trigger {trigger} not present"
                f" in bindings {bindings}")

        if isinstance(trigger, HttpTrigger) and trigger.route is None:
            trigger.route = self._function.get_function_name()

    def build(self) -> Function:
        self._validate_function()
        return self._function


class FunctionApp:
    """FunctionApp object used by worker function indexing model captures
    user defined functions and metadata.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self, auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`FunctionApp` object.

        :param auth_level: defaults to AuthLevel.FUNCTION, takes str or
        AuthLevel
        """
        self._function_builders: List[FunctionBuilder] = []
        self._app_script_file: str = SCRIPT_FILE_NAME
        self._auth_level = AuthLevel[auth_level] \
            if isinstance(auth_level, str) else auth_level

    @property
    def app_script_file(self) -> str:
        """Name of function app script file in which all the functions
         are defined.

        :return: Script file name.
        """
        return self._app_script_file

    @property
    def auth_level(self) -> AuthLevel:
        """Authorization level of the function app. Will be applied to the http
         trigger functions which
        do not have authorization level specified.

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
                f"Unsupported type for function app decorator found.")
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

    def route(self,
              route: Optional[str] = None,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              trigger_arg_data_type: Optional[Union[DataType, str]] = None,
              output_arg_data_type: Optional[Union[DataType, str]] = None,
              methods: Optional[
                  Union[Iterable[str], Iterable[HttpMethod]]] = None,
              auth_level: Optional[Union[AuthLevel, str]] = None) -> Callable:
        """The route decorator adds :class:`HttpTrigger` and
        :class:`HttpOutput` binding to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining HttpTrigger
        and HttpOutput binding in the function.json which enables your
        function be triggered when http requests hit the specified route.

        Ref: https://aka.ms/azure-function-binding-http

        :param route: Route for the http endpoint, if None, it will be set
        to function name if present or user defined python function name.
        :param trigger_arg_name: Argument name for :class:`HttpRequest`,
        defaults to 'req'.
        :param binding_arg_name: Argument name for :class:`HttpResponse`,
        defaults to '$return'.
        :param trigger_arg_data_type: Defines how Functions runtime should
        treat the trigger_arg_name value, defaults to DataType.UNDEFINED.
        :param output_arg_data_type: Defines how Functions runtime should
        treat the binding_arg_name value, defaults to DataType.UNDEFINED.
        :param methods: A tuple of the HTTP methods to which the function
        responds.
        :param auth_level: Determines what keys, if any, need to be present
        on the request in order to invoke the function. If not specified,
        it will be set to :class:`FunctionApp` object auth level.
        :return: Decorator function.
        """

        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                nonlocal auth_level
                if auth_level is None:
                    auth_level = self.auth_level

                fb.add_trigger(trigger=HttpTrigger(
                    name=trigger_arg_name,
                    data_type=parse_singular_param_to_enum(
                        trigger_arg_data_type,
                        DataType),
                    methods=parse_iterable_param_to_enum(methods, HttpMethod),
                    auth_level=parse_singular_param_to_enum(auth_level,
                                                            AuthLevel),
                    route=route))
                fb.add_binding(binding=HttpOutput(
                    name=binding_arg_name,
                    data_type=parse_singular_param_to_enum(
                        output_arg_data_type,
                        DataType)))
                return fb

            return decorator()

        return wrap

    def schedule(self,
                 arg_name: str,
                 schedule: str,
                 run_on_startup: Optional[bool] = None,
                 use_monitor: Optional[bool] = None,
                 data_type: Optional[Union[DataType, str]] = None) -> Callable:
        """The schedule decorator adds :class:`TimerTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TimerTrigger
        in the function.json which enables your function be triggered on the
        specified schedule.

        Ref: https://aka.ms/azure-function-binding-timer

        :param arg_name: The name of the variable that represents the
        :class:`TimerRequest` object in function code.
        :param schedule: A string representing a CRON expression that will
        be used to schedule a function to run.
        :param run_on_startup: If true, the function is invoked when the
        runtime starts, defaults to False.
        :param use_monitor: Set to true or false to indicate whether the
        schedule should be monitored, defaults to False.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
                                                               DataType)))
                return fb

            return decorator()

        return wrap

    def on_service_bus_queue_change(
            self,
            arg_name: str,
            connection: str,
            queue_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None) -> Callable:
        """The on_service_bus_queue_change decorator adds
        :class:`ServiceBusQueueTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueTrigger
        in the function.json which enables your function be triggered when
        new message(s) are sent to the service bus queue.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string,
        defaults to AccessRights.MANAGE
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription, defaults to False
        :param cardinality: Set to many in order to enable batching. If
        omitted or set to one, a single message is passed to the function,
        defaults to Cardinality.ONE.
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
                                                                 Cardinality)))
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
                                    AccessRights, str]] = None) -> Callable:
        """The write_service_bus_queue decorator adds
        :class:`ServiceBusQueueOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusQueueOutput
        in the function.json which enables function to write message(s) to
        the service bus queue.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus queue output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param queue_name: Name of the queue to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string,
        defaults to AccessRights.MANAGE
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
                            access_rights, AccessRights)))
                return fb

            return decorator()

        return wrap

    def on_service_bus_topic_change(
            self,
            arg_name: str,
            connection: str,
            topic_name: str,
            subscription_name: str,
            data_type: Optional[Union[DataType, str]] = None,
            access_rights: Optional[Union[AccessRights, str]] = None,
            is_sessions_enabled: Optional[bool] = None,
            cardinality: Optional[Union[Cardinality, str]] = None) -> Callable:
        """The on_service_bus_topic_change decorator adds
        :class:`ServiceBusTopicTrigger` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the service bus topic.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents the
        :class:`ServiceBusMessage` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string,
        defaults to AccessRights.MANAGE
        :param is_sessions_enabled: True if connecting to a session-aware
        queue or subscription, defaults to False
        :param cardinality: Set to many in order to enable batching. If
        omitted or set to one, a single message is passed to the function,
        defaults to Cardinality.ONE.
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
                                                                 Cardinality)))
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
                                    AccessRights, str]] = None) -> Callable:
        """The write_service_bus_topic decorator adds
        :class:`ServiceBusTopicOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining ServiceBusTopicOutput
        in the function.json which enables function to write message(s) to
        the service bus topic.

        Ref: https://aka.ms/azure-function-binding-service-bus

        :param arg_name: The name of the variable that represents service
        bus topic output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Service Bus.
        :param topic_name: Name of the topic to monitor.
        :param subscription_name: Name of the subscription to monitor.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param access_rights: Access rights for the connection string,
        defaults to AccessRights.MANAGE
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
                            AccessRights)))
                return fb

            return decorator()

        return wrap

    def on_queue_change(self,
                        arg_name: str,
                        queue_name: str,
                        connection: str,
                        data_type: Optional[DataType] = None) -> Callable:
        """The on_queue_change decorator adds :class:`QueueTrigger` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the storage queue.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents the
        :class:`QueueMessage` object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
                                                               DataType)))
                return fb

            return decorator()

        return wrap

    def write_queue(self,
                    arg_name: str,
                    queue_name: str,
                    connection: str,
                    data_type: Optional[DataType] = None) -> Callable:
        """The write_queue decorator adds :class:`QueueOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining QueueOutput
        in the function.json which enables function to write message(s) to
        the storage queue.

        Ref: https://aka.ms/azure-function-binding-queue

        :param arg_name: The name of the variable that represents storage
        queue output object in function code.
        :param queue_name: The name of the queue to poll.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Azure Queues.
        :param data_type: Set to many in order to enable batching. If
        omitted or set to one, a single message is passed to the function,
        defaults to Cardinality.ONE.
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
                                            data_type, DataType)))
                return fb

            return decorator()

        return wrap

    def on_event_hub_message(self,
                             arg_name: str,
                             connection: str,
                             event_hub_name: str,
                             data_type: Optional[Union[DataType, str]] = None,
                             cardinality: Optional[
                                 Union[Cardinality, str]] = None,
                             consumer_group: Optional[str] = None) -> Callable:
        """The on_event_hub_message decorator adds :class:`EventHubTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubTrigger
        in the function.json which enables function to be triggered when new
        message(s) are sent to the event hub.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents
        :class:`EventHubEvent` object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hubs.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
        :param cardinality: Set to many in order to enable batching. If
        omitted or set to one, a single message is passed to the function,
        defaults to Cardinality.MANY.
        :param consumer_group: An optional property that sets the consumer
        group used to subscribe to events in the hub. If omitted,
        the $Default consumer group is used.
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
                        consumer_group=consumer_group))
                return fb

            return decorator()

        return wrap

    def write_event_hub_message(self,
                                arg_name: str,
                                connection: str,
                                event_hub_name: str,
                                data_type: Optional[
                                    Union[DataType, str]] = None) -> Callable:
        """The write_event_hub_message decorator adds
        :class:`EventHubOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining EventHubOutput
        in the function.json which enables function to write message(s) to
        the event hub.

        Ref: https://aka.ms/azure-function-binding-event-hubs

        :param arg_name: The name of the variable that represents event hub
        output object in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to Event Hub.
        :param event_hub_name: The name of the event hub.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
                                                               DataType)))
                return fb

            return decorator()

        return wrap

    def on_cosmos_db_update(self,
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
                                Union[DataType, str]] = None) -> \
            Callable:
        """The on_cosmos_db_update decorator adds :class:`CosmosDBTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBTrigger
        in the function.json which enables function to be triggered when
        CosmosDB data is changed.

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
        already exist, defaults to False.
        :param leases_collection_throughput: Defines the number of Request
        Units to assign when the leases collection is created, defaults to -1.
        :param lease_collection_prefix: When set, the value is added as a
        prefix to the leases created in the Lease collection for this
        Function, defaults to None.
        :param checkpoint_interval: When set, it defines, in milliseconds,
        the interval between lease checkpoints. Default is always after a
        Function call.
        :param checkpoint_document_count: Customizes the amount of documents
        between lease checkpoints. Default is always after a Function call.
        :param feed_poll_delay: The time (in milliseconds) for the delay
        between polling a partition for new changes on the feed, after all
        current changes are drained. Default is 5,000 milliseconds,
        or 5 seconds.
        :param lease_renew_interval: When set, it defines, in milliseconds,
        the renew interval for all leases for partitions currently held by
        an instance. Default is 17000 (17 seconds).
        :param lease_acquire_interval: When set, it defines,
        in milliseconds, the interval to kick off a task to compute if
        partitions are distributed evenly among known host instances.
        Default is 13000 (13 seconds).
        :param lease_expiration_interval: When set, it defines,
        in milliseconds, the interval for which the lease is taken on a
        lease representing a partition. Default is 60000 (60 seconds).
        :param max_items_per_invocation: When set, this property sets the
        maximum number of items received per Function call, defaults to -1.
        :param start_from_beginning: This option tells the Trigger to read
        changes from the beginning of the collection's change history
        instead of starting at the current time, defaults to False.
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service,
        defaults to "".
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
            create_lease_collection_if_not_exists # NoQA
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
            data_type=parse_singular_param_to_enum(data_type, DataType))

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
                                      Union[DataType, str]] = None) \
            -> Callable:
        """The write_cosmos_db_documents decorator adds
        :class:`CosmosDBOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBOutput
        in the function.json which enables function to write to the CosmosDB.

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
        collection is created when it doesn't exist, defaults to False.
        :param partition_key: When CreateIfNotExists is true, it defines the
        partition key path for the created collection, defaults to None.
        :param collection_throughput: When CreateIfNotExists is true,
        it defines the throughput of the created collection, defaults to -1.
        :param use_multiple_write_locations: When set to true along with
        PreferredLocations, it can leverage multi-region writes in the Azure
        Cosmos DB service, defaults to False
        :param preferred_locations: Defines preferred locations (regions)
        for geo-replicated database accounts in the Azure Cosmos DB service,
        defaults to None.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
                        use_multiple_write_locations # NoQA
                        =use_multiple_write_locations,
                        preferred_locations=preferred_locations,
                        data_type=parse_singular_param_to_enum(data_type,
                                                               DataType)))
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
                                     Union[DataType, str]] = None) \
            -> Callable:
        """The read_cosmos_db_documents decorator adds
        :class:`CosmosDBInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining CosmosDBInput
        in the function.json which enables function to read from CosmosDB.

        Ref: https://aka.ms/azure-function-binding-cosmosdb-v2

        :param arg_name: The name of the variable that represents
        :class:`DocumentList` input object in function code.
        :param database_name: The database containing the document.
        :param collection_name: The name of the collection that contains the
        document.
        :param connection_string_setting: The name of the app setting
        containing your Azure Cosmos DB connection string.
        :param id: The ID of the document to retrieve, defaults to
        None.
        :param sql_query: An Azure Cosmos DB SQL query used for retrieving
        multiple documents, defaults to None.
        :param partition_key: Specifies the partition key value for the
        lookup, defaults to None.
        :param data_type: Defines how Functions runtime should treat the
        parameter value, defaults to DataType.UNDEFINED.
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
                                                               DataType)))
                return fb

            return decorator()

        return wrap
