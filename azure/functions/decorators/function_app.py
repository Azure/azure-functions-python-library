#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import operator
from functools import reduce
from typing import Callable, Dict, List, Optional, Union, Tuple

from azure.functions.decorators.core import Binding, Trigger, DataType, \
    AuthLevel, HttpMethod, SCRIPT_FILE_NAME
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput
from azure.functions.decorators.eventhub import EventHubTrigger, EventHubOutput
from azure.functions.decorators.http import HttpTrigger, HttpOutput
from azure.functions.decorators.queue import QueueTrigger, QueueOutput
from azure.functions.decorators.servicebus import ServiceBusQueueTrigger, \
    ServiceBusQueueOutput, ServiceBusTopicTrigger, \
    ServiceBusTopicOutput
from azure.functions.decorators import Cardinality, AccessRights
from azure.functions.decorators.timer import TimerTrigger
from azure.functions.http import HttpRequest
from azure.functions._http import HttpResponse
from azure.functions._http_wsgi import WsgiMiddleware, Context

GET = HttpMethod.GET
POST = HttpMethod.POST


class Function(object):
    def __init__(self, func: Callable, script_file):
        self._name = func.__name__
        self._func = func
        self._trigger: Optional[Trigger] = None
        self._bindings: List[Binding] = []

        self.function_script_file = script_file

    def add_binding(self, binding: Binding):
        self._bindings.append(binding)

    def add_trigger(self, trigger: Trigger):
        if self._trigger:
            raise ValueError("A trigger was already registered to this "
                             "function. Adding another trigger is not the "
                             "correct behavior as a function can only have one"
                             " trigger. Existing registered trigger "
                             f"is {self._trigger} and New trigger "
                             f"being added is {trigger}")

        self._trigger = trigger

        #  We still add the trigger info to the bindings to ensure that
        #  function.json is complete
        self._bindings.append(trigger)

    def set_function_name(self, function_name: str = None):
        if function_name:
            self._name = function_name

    def get_trigger(self):
        return self._trigger

    def get_bindings(self):
        return self._bindings

    def get_bindings_dict(self):
        stub_bindings_f_json: Dict[str, List[Dict]] = {"bindings": []}
        for b in self._bindings:
            stub_bindings_f_json["bindings"].append(b.get_dict_repr())
        return stub_bindings_f_json

    def get_dict_repr(self):
        stub_f_json: Dict[str, Union[List[str], str]] = {
            "scriptFile": self.function_script_file
        }
        stub_f_json.update(self.get_bindings_dict())  # NoQA
        return stub_f_json

    def get_user_function(self):
        return self._func

    def get_function_name(self):
        return self._name

    def get_function_json(self):
        return json.dumps(self.get_dict_repr())

    def __str__(self):
        return self.get_function_json()


class FunctionBuilder(object):
    def __init__(self, func, function_script_file):
        self._function = Function(func, function_script_file)

    def __call__(self, *args, **kwargs):
        pass

    def configure_function_name(self, function_name: str):
        self._function.set_function_name(function_name)

        return self

    def add_trigger(self, trigger: Trigger):
        self._function.add_trigger(trigger=trigger)
        return self

    def add_binding(self, binding: Binding):
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

    def build(self):
        self._validate_function()
        return self._function


class FunctionsApp:
    def __init__(self, auth_level: AuthLevel = AuthLevel.FUNCTION):
        self._function_builders: List[FunctionBuilder] = []
        self._app_script_file = SCRIPT_FILE_NAME
        self._auth_level = auth_level

    @property
    def app_script_file(self):
        return self._app_script_file

    @property
    def auth_level(self):
        return self._auth_level

    def get_functions(self) -> List[Function]:
        return [function_builder.build() for function_builder
                in self._function_builders]

    def _validate_type(self, func):
        if isinstance(func, FunctionBuilder):
            fb = self._function_builders.pop()
        elif callable(func):
            fb = FunctionBuilder(func, self._app_script_file)
        else:
            raise ValueError(
                f"Unsupported type for function app decorator found.")
        return fb

    def _configure_function_builder(self, wrap):
        def decorator(func):
            fb = self._validate_type(func)
            self._function_builders.append(fb)
            return wrap(fb)

        return decorator

    def function_name(self, name: str):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.configure_function_name(name)
                return fb

            return decorator()

        return wrap

    def flask(self, app, auth_level: Optional[AuthLevel] = None):

        methods = reduce(operator.or_,
                         [rule.methods for rule in
                          app.url_map.iter_rules()])
        methods = tuple(HttpMethod(m.upper()) for m in methods if
                        m.upper() in HttpMethod.__members__)

        @self.route(methods=methods, auth_level=auth_level, route="/{*route}")
        def main(req: HttpRequest, context: Context) -> HttpResponse:
            return WsgiMiddleware(app.wsgi_app).handle(req, context)

    def route(self,
              trigger_arg_name: str = 'req',
              binding_arg_name: str = '$return',
              trigger_arg_data_type: DataType = DataType.UNDEFINED,
              output_arg_data_type: DataType = DataType.UNDEFINED,
              methods: Tuple[HttpMethod, ...] = (GET, POST),
              auth_level: Optional[AuthLevel] = None,
              route: Optional[str] = None):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                nonlocal auth_level
                if auth_level is None:
                    auth_level = self.auth_level

                fb.add_trigger(trigger=HttpTrigger(
                    name=trigger_arg_name,
                    data_type=trigger_arg_data_type,
                    methods=methods,
                    auth_level=auth_level,
                    route=route))
                fb.add_binding(binding=HttpOutput(
                    name=binding_arg_name,
                    data_type=output_arg_data_type))
                return fb

            return decorator()

        return wrap

    def schedule(self,
                 arg_name: str,
                 schedule: str,
                 run_on_startup: bool = False,
                 use_monitor: bool = False,
                 data_type: DataType = DataType.UNDEFINED):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=TimerTrigger(name=arg_name,
                                         schedule=schedule,
                                         run_on_startup=run_on_startup,
                                         use_monitor=use_monitor,
                                         data_type=data_type))
                return fb

            return decorator()

        return wrap

    def on_service_bus_queue_change(
            self,
            arg_name: str,
            connection: str,
            queue_name: str,
            data_type: DataType = DataType.UNDEFINED,
            access_rights: AccessRights =
            AccessRights.MANAGE,
            is_sessions_enabled: bool = False,
            cardinality: Cardinality = Cardinality.ONE):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusQueueTrigger(
                        name=arg_name,
                        connection=connection,
                        queue_name=queue_name,
                        data_type=data_type,
                        access_rights=access_rights,
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=cardinality))
                return fb

            return decorator()

        return wrap

    def write_service_bus_queue(self,
                                arg_name: str,
                                connection: str,
                                queue_name: str,
                                data_type: DataType = DataType.UNDEFINED,
                                access_rights: AccessRights =
                                AccessRights.MANAGE):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusQueueOutput(name=arg_name,
                                                  connection=connection,
                                                  queue_name=queue_name,
                                                  data_type=data_type,
                                                  access_rights=access_rights))
                return fb

            return decorator()

        return wrap

    def on_service_bus_topic_change(
            self,
            arg_name: str,
            connection: str,
            topic_name: str,
            subscription_name: str,
            data_type: DataType = DataType.UNDEFINED,
            access_rights: AccessRights =
            AccessRights.MANAGE,
            is_sessions_enabled: bool = False,
            cardinality: Cardinality = Cardinality.ONE):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=ServiceBusTopicTrigger(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=data_type,
                        access_rights=access_rights,
                        is_sessions_enabled=is_sessions_enabled,
                        cardinality=cardinality))
                return fb

            return decorator()

        return wrap

    def write_service_bus_topic(self,
                                arg_name: str,
                                connection: str,
                                topic_name: str,
                                subscription_name: str,
                                data_type: DataType = DataType.UNDEFINED,
                                access_rights: AccessRights =
                                AccessRights.MANAGE):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=ServiceBusTopicOutput(
                        name=arg_name,
                        connection=connection,
                        topic_name=topic_name,
                        subscription_name=subscription_name,
                        data_type=data_type,
                        access_rights=access_rights))
                return fb

            return decorator()

        return wrap

    def on_queue_change(self,
                        arg_name: str,
                        queue_name: str,
                        connection: str,
                        data_type: DataType = DataType.UNDEFINED):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=QueueTrigger(name=arg_name,
                                         queue_name=queue_name,
                                         connection=connection,
                                         data_type=data_type))
                return fb

            return decorator()

        return wrap

    def write_queue(self,
                    arg_name: str,
                    queue_name: str,
                    connection: str,
                    data_type: DataType = DataType.UNDEFINED):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=QueueOutput(name=arg_name,
                                        queue_name=queue_name,
                                        connection=connection,
                                        data_type=data_type))
                return fb

            return decorator()

        return wrap

    def on_event_hub_message(self,
                             arg_name: str,
                             connection: str,
                             event_hub_name: str,
                             data_type: DataType = DataType.UNDEFINED,
                             cardinality: Cardinality = Cardinality.MANY,
                             consumer_group: str = "$Default"):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_trigger(
                    trigger=EventHubTrigger(name=arg_name,
                                            connection=connection,
                                            event_hub_name=event_hub_name,
                                            data_type=data_type,
                                            cardinality=cardinality,
                                            consumer_group=consumer_group))
                return fb

            return decorator()

        return wrap

    def write_event_hub_message(self,
                                arg_name: str,
                                connection: str,
                                event_hub_name: str,
                                data_type: DataType =
                                DataType.UNDEFINED):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=EventHubOutput(name=arg_name,
                                           connection=connection,
                                           event_hub_name=event_hub_name,
                                           data_type=data_type))
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
                            create_lease_collection_if_not_exists:
                            bool = False,
                            leases_collection_throughput: int = -1,
                            lease_collection_prefix: Optional[str] = None,
                            checkpoint_interval: int = -1,
                            checkpoint_document_count: int = -1,
                            feed_poll_delay: int = 5000,
                            lease_renew_interval: int = 17000,
                            lease_acquire_interval: int = 13000,
                            lease_expiration_interval: int = 60000,
                            max_items_per_invocation: int = -1,
                            start_from_beginning: bool = False,
                            preferred_locations: str = "",
                            data_type: DataType = DataType.UNDEFINED):
        trigger = CosmosDBTrigger(
            name=arg_name,
            database_name=database_name,
            collection_name=collection_name,
            connection_string_setting=connection_string_setting,
            lease_collection_name=lease_collection_name,
            lease_conn_str_setting=lease_connection_string_setting,
            lease_database_name=lease_database_name,
            create_lease_coll_if_unset=create_lease_collection_if_not_exists,
            lease_coll_throughput=leases_collection_throughput,
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
            data_type=data_type)

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
                                  create_if_not_exists: bool = False,
                                  partition_key: Optional[str] = None,
                                  collection_throughput: int = -1,
                                  use_multiple_write_locations: bool = False,
                                  preferred_locations: Optional[str] = None,
                                  data_type: DataType = DataType.UNDEFINED):
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
                        use_multiple_write_loc=use_multiple_write_locations,
                        preferred_locations=preferred_locations,
                        data_type=data_type))
                return fb

            return decorator()

        return wrap

    def read_cosmos_db_documents(self,
                                 arg_name: str,
                                 database_name: str,
                                 collection_name: str,
                                 connection_string_setting: str,
                                 document_id: Optional[str] = None,
                                 sql_query: Optional[str] = None,
                                 partition_key: Optional[str] = None,
                                 data_type: DataType = DataType.UNDEFINED):
        @self._configure_function_builder
        def wrap(fb):
            def decorator():
                fb.add_binding(
                    binding=CosmosDBInput(
                        name=arg_name,
                        database_name=database_name,
                        collection_name=collection_name,
                        connection_string_setting=connection_string_setting,
                        document_id=document_id,
                        sql_query=sql_query,
                        partition_key=partition_key,
                        data_type=data_type))
                return fb

            return decorator()

        return wrap
