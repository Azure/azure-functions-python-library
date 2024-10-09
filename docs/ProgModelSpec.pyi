#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from abc import ABC
from typing import Callable, Dict, List, Optional, Union, Iterable

from azure.functions import AsgiMiddleware, WsgiMiddleware
from azure.functions.decorators.core import Binding, BlobSource, Trigger, DataType, \
    AuthLevel, Cardinality, AccessRights, Setting
from azure.functions.decorators.function_app import FunctionBuilder, SettingsApi
from azure.functions.decorators.http import HttpMethod


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
        pass

    def add_binding(self, binding: Binding) -> None:
        """Add a binding instance to the function.

        :param binding: The binding object to add.
        """
        pass

    def add_trigger(self, trigger: Trigger) -> None:
        """Add a trigger instance to the function.

        :param trigger: The trigger object to add.
        :raises ValueError: Raises trigger already exists error if a trigger is
             being added to a function which has trigger attached.
        """

        pass

    def get_trigger(self) -> Optional[Trigger]:
        """Get attached trigger instance of the function.

        :return: Trigger instance or None.
        """
        pass

    def get_bindings(self) -> List[Binding]:
        """Get all the bindings attached to the function.

        :return: Bindings attached to the function.
        """
        pass

    def get_raw_bindings(self) -> List[str]:
        pass

    def get_bindings_dict(self) -> Dict:
        """Get dictionary representation of the bindings of the function.

        :return: Dictionary representation of the bindings.
        """
        pass

    def get_dict_repr(self) -> Dict:
        """Get the dictionary representation of the function.

        :return: The dictionary representation of the function.
        """
        pass

    def get_user_function(self) -> Callable:
        """Get the python function customer defined.

        :return: The python function customer defined.
        """
        pass

    def get_function_name(self) -> str:
        """Get the function name.

        :return: Function name.
        """
        pass

    def get_setting(self, setting_name: str) -> Optional[Setting]:
        """Get a specific setting attached to the function.

        :param setting_name: The name of the setting to search for.
        :return: The setting attached to the function (or None if not found).
        """
        pass

    def get_function_json(self) -> str:
        """Get the json stringified form of function.

        :return: The json stringified form of function.
        """
        pass

    def __str__(self):
        pass

class DecoratorApi(ABC):
    """Interface which contains essential decorator function building blocks
    to extend for creating new function app or blueprint classes.
    """

    def __init__(self, *args, **kwargs):
        pass

    @property
    def app_script_file(self) -> str:
        """Name of function app script file in which all the functions
         are defined. \n
         Script file defined here is for placeholder purpose, please refer to
         worker defined script file path as the single point of truth.

        :return: Script file name.
        """
        pass

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
        pass

    def _configure_function_builder(self, wrap) -> Callable:
        """Decorator function on user defined function to create and return
         :class:`FunctionBuilder` object from :class:`Callable` func.
        """
        pass

    def function_name(self, name: str) -> Callable:
        """Set name of the :class:`Function` object.

        :param name: Name of the function.
        :return: Decorator function.
        """

        pass


class HttpFunctionsAuthLevelMixin(ABC):
    """Interface to extend for enabling function app level http
    authorization level setting"""

    def __init__(self, auth_level: Union[AuthLevel, str], *args, **kwargs):
        pass

    @property
    def auth_level(self):
        """Authorization level of the function app. Will be applied to the http
         trigger functions which do not have authorization level specified.

        :return: Authorization level of the function app.
        """

        pass


class TriggerApi(DecoratorApi, ABC):
    """Interface to extend for using existing trigger decorator functions."""

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

        pass

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

        pass

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

        pass

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

        pass

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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """
        pass

    def blob_trigger(self,
                     arg_name: str,
                     path: str,
                     connection: str,
                     source: Optional[BlobSource] = None,
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
        :param source: Sets the source of the triggering event. 
        Use EventGrid for an Event Grid-based blob trigger, 
        which provides much lower latency. 
        The default is LogsAndContainerScan, 
        which uses the standard polling mechanism to detect changes 
        in the container.
        :param data_type: Defines how Functions runtime should treat the
        parameter value.
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

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

        pass

    def sql_trigger(self,
                    arg_name: str,
                    table_name: str,
                    connection_string_setting: str,
                    leases_table_name: Optional[str] = None,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable[..., Any]:
        """The sql_trigger decorator adds :class:`SqlTrigger`
        to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlTrigger in the function.json which
        enables function to be triggered when there are changes in the Sql
        table.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
        :class:`SqlRowList` object in the function code
        :param table_name: The name of the table monitored by the trigger
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param leases_table_name: The name of the table used to store
        leases. If not specified, the leases table name will be
        Leases_{FunctionId}_{TableId}.
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        pass

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

        pass


class BindingApi(DecoratorApi, ABC):
    """Interface to extend for using existing binding decorator functions."""

    def service_bus_queue_output(self,
                                 arg_name: str,
                                 connection: str,
                                 queue_name: str,
                                 data_type: Optional[
                                    Union[DataType, str]] = None,
                                 access_rights: Optional[Union[
                                    AccessRights, str]] = None,
                                 **kwargs) -> \
            Callable:
        """The service_bus_queue_output decorator adds
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

        pass

    def service_bus_topic_output(self,
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
        """The service_bus_topic_output decorator adds
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

        pass

    def queue_output(self,
                     arg_name: str,
                     queue_name: str,
                     connection: str,
                     data_type: Optional[DataType] = None,
                     **kwargs) -> Callable:
        """The queue_output decorator adds :class:`QueueOutput` to the
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

    def event_hub_output(self,
                         arg_name: str,
                         connection: str,
                         event_hub_name: str,
                         data_type: Optional[
                                    Union[DataType, str]] = None,
                         **kwargs) -> \
            Callable:
        """The event_hub_output decorator adds
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

    def cosmos_db_output(self,
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
        """The cosmos_db_output decorator adds
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

    def cosmos_db_input(self,
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
        """The cosmos_db_input decorator adds
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

    def blob_input(self,
                   arg_name: str,
                   path: str,
                   connection: str,
                   data_type: Optional[DataType] = None,
                   **kwargs) -> Callable:
        """
        The blob_input decorator adds :class:`BlobInput` to the
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.

        :return: Decorator function.
        """

        pass

    def blob_output(self,
                    arg_name: str,
                    path: str,
                    connection: str,
                    data_type: Optional[DataType] = None,
                    **kwargs) -> Callable:
        """
        The blob_output decorator adds :class:`BlobOutput` to the
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
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json.
        :return: Decorator function.
        """

        pass

    def event_grid_output(self,
                          arg_name: str,
                          topic_endpoint_uri: str,
                          topic_key_setting: str,
                          data_type: Optional[
                             Union[DataType, str]] = None,
                          **kwargs) -> Callable:
        """
        The event_grid_output decorator adds
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

        pass

    def table_input(self,
                    arg_name: str,
                    connection: str,
                    table_name: str,
                    row_key: Optional[str] = None,
                    partition_key: Optional[str] = None,
                    take: Optional[int] = None,
                    filter: Optional[str] = None,
                    data_type: Optional[
                       Union[DataType, str]] = None) -> Callable:
        """
        The table_input decorator adds :class:`TableInput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TableInput
        in the function.json which enables function to read a table in
        an Azure Storage or Cosmos DB account
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents
        the table or entity in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to the table service.
        :param table_name: The Name of the table
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param take: The maximum number of entities to return
        :param filter: An OData filter expression for the entities to return
         from the table.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :return: Decorator function.
        """

        pass

    def table_output(self,
                     arg_name: str,
                     connection: str,
                     table_name: str,
                     row_key: str,
                     partition_key: str,
                     data_type: Optional[
                        Union[DataType, str]] = None) -> Callable:

        """
        The table_output decorator adds :class:`TableOutput` to the
        :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This is equivalent to defining TableOutput
        in the function.json which enables function to write entities
        to a table in an Azure Storage
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/tablesbindings

        :param arg_name: The name of the variable that represents
        the table or entity in function code.
        :param connection: The name of an app setting or setting collection
        that specifies how to connect to the table service.
        :param table_name: The Name of the table
        :param row_key: The row key of the table entity to read.
        :param partition_key: The partition key of the table entity to read.
        :param data_type: Defines how Functions runtime should treat the
         parameter value.
        :return: Decorator function.
        """

        pass

    def sql_input(self,
                  arg_name: str,
                  command_text: str,
                  connection_string_setting: str,
                  command_type: Optional[str] = 'Text',
                  parameters: Optional[str] = None,
                  data_type: Optional[DataType] = None,
                  **kwargs) -> Callable[..., Any]:
        """The sql_input decorator adds
        :class:`SqlInput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlInput in the function.json which
        enables the function to read from a Sql database.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents a
        :class:`SqlRowList` input object in function code
        :param command_text: The Transact-SQL query command or name of the
        stored procedure executed by the binding
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param command_type: A CommandType value, which is Text for a query
        and StoredProcedure for a stored procedure
        :param parameters: Zero or more parameter values passed to the
        command during execution as a single string. Must follow the format
        @param1=param1,@param2=param2
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        pass

    def sql_output(self,
                   arg_name: str,
                   command_text: str,
                   connection_string_setting: str,
                   data_type: Optional[DataType] = None,
                   **kwargs) -> Callable[..., Any]:
        """The sql_output decorator adds
        :class:`SqlOutput` to the :class:`FunctionBuilder` object
        for building :class:`Function` object used in worker function
        indexing model. This decorator will work only with extension bundle 4.x
        and above.
        This is equivalent to defining SqlOutput in the function.json which
        enables the function to write to a Sql database.
        All optional fields will be given default value by function host when
        they are parsed by function host.

        Ref: https://aka.ms/sqlbindings

        :param arg_name: The name of the variable that represents
        Sql output object in function code
        :param command_text: The Transact-SQL query command or name of the
        stored procedure executed by the binding
        :param connection_string_setting: The name of an app setting that
        contains the connection string for the database against which the
        query or stored procedure is being executed
        :param data_type: Defines how Functions runtime should treat the
        parameter value
        :param kwargs: Keyword arguments for specifying additional binding
        fields to include in the binding json

        :return: Decorator function.
        """

        pass

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

        pass

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

        pass


class FunctionRegister(DecoratorApi, HttpFunctionsAuthLevelMixin, ABC):
    def __init__(self, auth_level: Union[AuthLevel, str], *args, **kwargs):
        """Interface for declaring top level function app class which will
        be directly indexed by Python Function runtime.

        :param auth_level: Determines what keys, if any, need to be present
        on the request in order to invoke the function.
        :param args: Variable length argument list.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def get_functions(self) -> List[Function]:
        """Get the function objects in the function app.

        :return: List of functions in the function app.
        """
        pass

    def register_functions(self, functions: DecoratorApi) -> None:
        """Register a list of functions in the function app.

        :param functions: Instance extending :class:`DecoratorApi` which
        contains a list of functions.
        """
        pass


class FunctionApp(FunctionRegister, TriggerApi, BindingApi):
    """FunctionApp object used by worker function indexing model captures
    user defined functions and metadata.

    Ref: https://aka.ms/azure-function-ref
    """

    def __init__(self,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION):
        """Constructor of :class:`FunctionApp` object.

        :param http_auth_level: Determines what keys, if any, need to be
        present
        on the request in order to invoke the function.
        """
        pass


class BluePrint(TriggerApi, BindingApi, SettingsApi):
    """Functions container class where all the functions
    loaded in it can be registered in :class:`FunctionRegister` subclasses
    but itself can not be indexed directly. The class contains all existing
    supported trigger and binding decorator functions.
    """
    pass


class ThirdPartyHttpFunctionApp(FunctionRegister, TriggerApi, ABC):
    """Interface to extend for building third party http function apps."""

    def _add_http_app(self,
                      http_middleware: Union[
                          AsgiMiddleware, WsgiMiddleware]) -> None:
        """Add a Wsgi or Asgi app integrated http function.

        :param http_middleware: :class:`AsgiMiddleware` or
        :class:`WsgiMiddleware` instance.

        :return: None
        """

        pass


class AsgiFunctionApp(ThirdPartyHttpFunctionApp):
    def __init__(self, app,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION,
                 prefix: str = ""):
        """Constructor of :class:`AsgiFunctionApp` object.

        :param app: asgi app object.
        """
        pass


class WsgiFunctionApp(ThirdPartyHttpFunctionApp):
    def __init__(self, app,
                 http_auth_level: Union[AuthLevel, str] = AuthLevel.FUNCTION,
                 prefix: str = ""):
        """Constructor of :class:`WsgiFunctionApp` object.

        :param app: wsgi app object.
        """
        pass
