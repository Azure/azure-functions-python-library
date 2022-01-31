#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest

from azure.functions.decorators import Cardinality, AccessRights
from azure.functions.decorators.core import DataType, AuthLevel, \
    BindingDirection, HttpMethod
from azure.functions.decorators.function_app import FunctionsApp
from azure.functions.decorators.http import HttpTrigger
from azure.functions.decorators.timer import TimerTrigger


class TestFunctionsApp(unittest.TestCase):
    def setUp(self):
        self.func_app = FunctionsApp()

    def test_route_is_function_name(self):
        app = self.func_app
        test_func_name = "dummy_function"

        @app.function_name(test_func_name)
        @app.route()
        def dummy_func():
            pass

        func = self._get_func(app)

        self.assertEqual(func.get_function_name(), test_func_name)
        self.assertTrue(isinstance(func.get_trigger(), HttpTrigger))
        self.assertTrue(func.get_trigger().route, test_func_name)

    def test_route_is_python_function_name(self):
        app = self.func_app

        @app.route()
        def dummy_func():
            pass

        func = self._get_func(app)

        self.assertEqual(func.get_function_name(), "dummy_func")
        self.assertTrue(isinstance(func.get_trigger(), HttpTrigger))
        self.assertTrue(func.get_trigger().route, "dummy_func")

    def test_route_is_custom(self):
        app = self.func_app

        @app.function_name("dummy_function")
        @app.route(route="dummy")
        def dummy_func():
            pass

        func = self._get_func(app)

        self.assertEqual(func.get_function_name(), "dummy_function")
        self.assertTrue(isinstance(func.get_trigger(), HttpTrigger))
        self.assertTrue(func.get_trigger().route, "dummy")

    def test_timer_trigger_default_args(self):
        app = self.func_app

        @app.schedule(arg_name="req", schedule="dummy_schedule")
        def dummy_func():
            pass

        func = self._get_func(app)
        self.assertEqual(func.get_function_name(), "dummy_func")
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "name": "req",
                    "type": "timerTrigger",
                    "dataType": str(DataType.UNDEFINED),
                    "direction": str(BindingDirection.IN),
                    "schedule": "dummy_schedule",
                    "runOnStartup": False,
                    "useMonitor": False
                }
            ]
        }))

    def test_timer_trigger_full_args(self):
        app = self.func_app

        @app.schedule(arg_name="req", schedule="dummy_schedule",
                      run_on_startup=False, use_monitor=False,
                      data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "name": "req",
                    "type": "timerTrigger",
                    "dataType": str(DataType.STRING),
                    "direction": str(BindingDirection.IN),
                    "schedule": "dummy_schedule",
                    "runOnStartup": False,
                    "useMonitor": False
                }
            ]
        }))

    def test_route_default_args(self):
        app = self.func_app

        @app.route()
        def dummy():
            pass

        func = self._get_func(app)
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "authLevel": "function",
                    "type": "httpTrigger",
                    "direction": str(BindingDirection.IN),
                    "name": "req",
                    "dataType": str(DataType.UNDEFINED),
                    "route": "dummy",
                    "methods": [
                        "GET", "POST"
                    ]
                },
                {
                    "type": "http",
                    "direction": str(BindingDirection.OUT),
                    "name": "$return",
                    "dataType": str(DataType.UNDEFINED)
                }
            ]
        }))

    def test_route_with_all_args(self):
        app = self.func_app

        @app.route(trigger_arg_name='trigger_name', binding_arg_name='out',
                   trigger_arg_data_type=DataType.STRING,
                   output_arg_data_type=DataType.STRING,
                   methods=(HttpMethod.GET, HttpMethod.PATCH),
                   auth_level=AuthLevel.FUNCTION, route='dummy_route')
        def dummy():
            pass

        func = self._get_func(app)
        self.assertEqual(str(func), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "authLevel": "function",
                    "type": "httpTrigger",
                    "direction": str(BindingDirection.IN),
                    "name": "trigger_name",
                    "dataType": str(DataType.STRING),
                    "route": "dummy_route",
                    "methods": [
                        "GET", "PATCH"
                    ]
                },
                {
                    "type": "http",
                    "direction": str(BindingDirection.OUT),
                    "name": "out",
                    "dataType": str(DataType.STRING)
                }
            ]
        }))

    def test_queue_default_args(self):
        app = self.func_app

        @app.on_queue_change(arg_name="req", queue_name="dummy_queue",
                             connection="dummy_conn")
        @app.write_queue(arg_name="out", queue_name="dummy_out_queue",
                         connection="dummy_out_conn")
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({"scriptFile": "function_app.py",
                                     "bindings": [
                                         {
                                             "type": "queue",
                                             "direction":
                                                 str(BindingDirection.OUT),
                                             "name": "out",
                                             "dataType":
                                                 str(DataType.UNDEFINED),
                                             "queueName": "dummy_out_queue",
                                             "connection": "dummy_out_conn"
                                         },
                                         {
                                             "type": "queueTrigger",
                                             "direction":
                                                 str(BindingDirection.IN),
                                             "name": "req",
                                             "dataType":
                                                 str(DataType.UNDEFINED),
                                             "queueName": "dummy_queue",
                                             "connection": "dummy_conn"
                                         }]}))

    def test_queue_full_args(self):
        app = self.func_app

        @app.on_queue_change(arg_name="req", queue_name="dummy_queue",
                             connection="dummy_conn",
                             data_type=DataType.STRING)
        @app.write_queue(arg_name="out", queue_name="dummy_out_queue",
                         connection="dummy_out_conn",
                         data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({"scriptFile": "function_app.py",
                                     "bindings": [
                                         {
                                             "type": "queue",
                                             "direction":
                                                 str(BindingDirection.OUT),
                                             "name": "out",
                                             "dataType": str(DataType.STRING),
                                             "queueName": "dummy_out_queue",
                                             "connection": "dummy_out_conn"
                                         },
                                         {
                                             "type": "queueTrigger",
                                             "direction":
                                                 str(BindingDirection.IN),
                                             "name": "req",
                                             "dataType": str(DataType.STRING),
                                             "queueName": "dummy_queue",
                                             "connection": "dummy_conn"
                                         }]}))

    def test_service_bus_queue_default_args(self):
        app = self.func_app

        @app.on_service_bus_queue_change(arg_name="req",
                                         connection="dummy_conn",
                                         queue_name="dummy_queue")
        @app.write_service_bus_queue(arg_name='res',
                                     connection='dummy_out_conn',
                                     queue_name='dummy_out_queue')
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "serviceBus",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "connection": "dummy_out_conn",
                                     "queueName": "dummy_out_queue",
                                     "dataType": str(DataType.UNDEFINED),
                                     "accessRights": "manage"
                                 },
                                 {
                                     "type": "serviceBusTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "connection": "dummy_conn",
                                     "queueName": "dummy_queue",
                                     "dataType": str(DataType.UNDEFINED),
                                     "accessRights": "manage",
                                     "isSessionsEnabled": False,
                                     "cardinality": "one"
                                 }
                             ]
                         }))

    def test_service_bus_queue_full_args(self):
        app = self.func_app

        @app.on_service_bus_queue_change(arg_name="req",
                                         connection="dummy_conn",
                                         queue_name="dummy_queue",
                                         data_type=DataType.STREAM,
                                         access_rights=AccessRights.MANAGE,
                                         is_sessions_enabled=True,
                                         cardinality=Cardinality.MANY)
        @app.write_service_bus_queue(arg_name='res',
                                     connection='dummy_out_conn',
                                     queue_name='dummy_out_queue',
                                     data_type=DataType.STREAM,
                                     access_rights=AccessRights.MANAGE)
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "serviceBus",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "connection": "dummy_out_conn",
                                     "queueName": "dummy_out_queue",
                                     "dataType": str(DataType.STREAM),
                                     "accessRights": "manage"
                                 },
                                 {
                                     "type": "serviceBusTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "connection": "dummy_conn",
                                     "queueName": "dummy_queue",
                                     "dataType": str(DataType.STREAM),
                                     "accessRights": "manage",
                                     "isSessionsEnabled": True,
                                     "cardinality": "many"
                                 }
                             ]
                         }))

    def test_service_bus_topic_default_args(self):
        app = self.func_app

        @app.on_service_bus_topic_change(arg_name='req',
                                         connection='dummy_conn',
                                         topic_name='dummy_topic',
                                         subscription_name='dummy_sub')
        @app.write_service_bus_topic(arg_name='res', connection='dummy_conn',
                                     topic_name='dummy_topic',
                                     subscription_name='dummy_sub')
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "serviceBus",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "connection": "dummy_conn",
                                     "topicName": "dummy_topic",
                                     "subscriptionName": "dummy_sub",
                                     "dataType": str(DataType.UNDEFINED),
                                     "accessRights": "manage"
                                 },
                                 {
                                     "type": "serviceBusTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "connection": "dummy_conn",
                                     "topicName": "dummy_topic",
                                     "subscriptionName": "dummy_sub",
                                     "dataType": str(DataType.UNDEFINED),
                                     "accessRights": "manage",
                                     "isSessionsEnabled": False,
                                     "cardinality": "one"
                                 }
                             ]
                         }))

    def test_service_bus_topic_full_args(self):
        app = self.func_app

        @app.on_service_bus_topic_change(arg_name='req',
                                         connection='dummy_conn',
                                         topic_name='dummy_topic',
                                         subscription_name='dummy_sub',
                                         data_type=DataType.STRING,
                                         access_rights=AccessRights.LISTEN,
                                         is_sessions_enabled=False,
                                         cardinality=Cardinality.MANY)
        @app.write_service_bus_topic(arg_name='res', connection='dummy_conn',
                                     topic_name='dummy_topic',
                                     subscription_name='dummy_sub',
                                     data_type=DataType.STRING,
                                     access_rights=AccessRights.LISTEN)
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "serviceBus",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "connection": "dummy_conn",
                                     "topicName": "dummy_topic",
                                     "subscriptionName": "dummy_sub",
                                     "dataType": str(DataType.STRING),
                                     "accessRights": "listen"
                                 },
                                 {
                                     "type": "serviceBusTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "connection": "dummy_conn",
                                     "topicName": "dummy_topic",
                                     "subscriptionName": "dummy_sub",
                                     "dataType": str(DataType.STRING),
                                     "accessRights": "listen",
                                     "isSessionsEnabled": False,
                                     "cardinality": "many"
                                 }
                             ]
                         }))

    def test_event_hub_default_args(self):
        app = self.func_app

        @app.on_event_hub_message(arg_name="req",
                                  connection="dummy_connection",
                                  event_hub_name="dummy_event_hub")
        @app.write_event_hub_message(arg_name="res",
                                     event_hub_name="dummy_event_hub",
                                     connection="dummy_connection")
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "eventHub",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "dataType": str(DataType.UNDEFINED),
                                     "connection": "dummy_connection",
                                     "eventHubName": "dummy_event_hub"
                                 },
                                 {
                                     "type": "eventHubTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "dataType": str(DataType.UNDEFINED),
                                     "connection": "dummy_connection",
                                     "eventHubName": "dummy_event_hub",
                                     "cardinality": "MANY",
                                     "consumerGroup": "$Default"
                                 }
                             ]
                         }))

    def test_event_hub_full_args(self):
        app = self.func_app

        @app.on_event_hub_message(arg_name="req",
                                  connection="dummy_connection",
                                  event_hub_name="dummy_event_hub",
                                  cardinality=Cardinality.ONE,
                                  consumer_group="dummy_group",
                                  data_type=DataType.UNDEFINED)
        @app.write_event_hub_message(arg_name="res",
                                     event_hub_name="dummy_event_hub",
                                     connection="dummy_connection",
                                     data_type=DataType.UNDEFINED)
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "eventHub",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "dataType": str(DataType.UNDEFINED),
                                     "connection": "dummy_connection",
                                     "eventHubName": "dummy_event_hub"
                                 },
                                 {
                                     "type": "eventHubTrigger",
                                     "direction": str(BindingDirection.IN),
                                     "name": "req",
                                     "dataType": str(DataType.UNDEFINED),
                                     "connection": "dummy_connection",
                                     "eventHubName": "dummy_event_hub",
                                     "cardinality": "ONE",
                                     "consumerGroup": "dummy_group"
                                 }
                             ]
                         }))

    def test_cosmosdb_full_args(self):
        app = self.func_app

        @app.on_cosmos_db_update(
            arg_name="trigger",
            database_name="dummy_db",
            collection_name="dummy_collection",
            connection_string_setting="dummy_str",
            lease_collection_name="dummy_lease_col",
            lease_connection_string_setting="dummy_lease_conn_str",
            lease_database_name="dummy_lease_db",
            leases_collection_throughput=1,
            lease_collection_prefix="dummy_lease_collection_prefix",
            checkpoint_interval=2,
            checkpoint_document_count=3,
            feed_poll_delay=4,
            lease_renew_interval=5,
            lease_acquire_interval=6,
            lease_expiration_interval=7,
            max_items_per_invocation=8,
            start_from_beginning=False,
            create_lease_collection_if_not_exists=False,
            preferred_locations="dummy_loc",
            data_type=DataType.STRING)
        @app.read_cosmos_db_documents(arg_name="in",
                                      database_name="dummy_in_db",
                                      collection_name="dummy_in_collection",
                                      connection_string_setting="dummy_str",
                                      document_id="dummy_id",
                                      sql_query="dummy_query",
                                      partition_key="dummy_partitions",
                                      data_type=DataType.STRING)
        @app.write_cosmos_db_documents(arg_name="out",
                                       database_name="dummy_out_db",
                                       collection_name="dummy_out_collection",
                                       connection_string_setting="dummy_str",
                                       create_if_not_exists=False,
                                       partition_key="dummy_part_key",
                                       collection_throughput=1,
                                       use_multiple_write_locations=False,
                                       preferred_locations="dummy_location",
                                       data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "out",
                                     "dataType": str(DataType.STRING),
                                     "databaseName": "dummy_out_db",
                                     "collectionName": "dummy_out_collection",
                                     "connectionStringSetting": "dummy_str",
                                     "createIfNotExists": False,
                                     "partitionKey": "dummy_part_key",
                                     "collectionThroughput": 1,
                                     "useMultipleWriteLocations": False,
                                     "preferredLocations": "dummy_location"
                                 },
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.IN),
                                     "name": "in",
                                     "dataType": str(DataType.STRING),
                                     "databaseName": "dummy_in_db",
                                     "collectionName": "dummy_in_collection",
                                     "collectionStringSetting": "dummy_str",
                                     "document_id": "dummy_id",
                                     "sqlQuery": "dummy_query",
                                     "partitionKey": "dummy_partitions"
                                 },
                                 {
                                     "type": "cosmosDBTrigger",
                                     "name": "trigger",
                                     "direction": str(BindingDirection.IN),
                                     "dataType": str(DataType.STRING),
                                     "leaseCollectionName":
                                         "dummy_lease_col",
                                     "leaseConnectionStringSetting":
                                         "dummy_lease_conn_str",
                                     "leaseDatabaseName": "dummy_lease_db",
                                     "createLeaseCollectionIfNotExists": False,
                                     "leasesCollectionThroughput": 1,
                                     "leaseCollectionPrefix":
                                         "dummy_lease_collection_prefix",
                                     "checkpointInterval": 2,
                                     "checkpointDocumentCount": 3,
                                     "feedPollDelay": 4,
                                     "leaseRenewInterval": 5,
                                     "leaseAcquireInterval": 6,
                                     "leaseExpirationInterval": 7,
                                     "maxItemsPerInvocation": 8,
                                     "startFromBeginning": False,
                                     "preferredLocations": "dummy_loc",
                                     "connectionStringSetting": "dummy_str",
                                     "databaseName": "dummy_db",
                                     "collectionName": "dummy_collection"
                                 }
                             ]
                         }))

    def test_cosmosdb_default_args(self):
        app = self.func_app

        @app.on_cosmos_db_update(arg_name="trigger", database_name="dummy_db",
                                 collection_name="dummy_collection",
                                 connection_string_setting="dummy_str")
        @app.read_cosmos_db_documents(arg_name="in",
                                      database_name="dummy_in_db",
                                      collection_name="dummy_in_collection",
                                      connection_string_setting="dummy_str")
        @app.write_cosmos_db_documents(arg_name="out",
                                       database_name="dummy_out_db",
                                       collection_name="dummy_out_collection",
                                       connection_string_setting="dummy_str")
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "out",
                                     "dataType": str(DataType.UNDEFINED),
                                     "databaseName": "dummy_out_db",
                                     "collectionName": "dummy_out_collection",
                                     "connectionStringSetting": "dummy_str",
                                     "createIfNotExists": False,
                                     "partitionKey": None,
                                     "collectionThroughput": -1,
                                     "useMultipleWriteLocations": False,
                                     "preferredLocations": None
                                 },
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.IN),
                                     "name": "in",
                                     "dataType": str(DataType.UNDEFINED),
                                     "databaseName": "dummy_in_db",
                                     "collectionName": "dummy_in_collection",
                                     "collectionStringSetting": "dummy_str",
                                     "document_id": None,
                                     "sqlQuery": None,
                                     "partitionKey": None
                                 },
                                 {
                                     "type": "cosmosDBTrigger",
                                     "name": "trigger",
                                     "direction": str(BindingDirection.IN),
                                     "dataType": str(DataType.UNDEFINED),
                                     "leaseCollectionName": None,
                                     "leaseConnectionStringSetting": None,
                                     "leaseDatabaseName": None,
                                     "createLeaseCollectionIfNotExists": False,
                                     "leasesCollectionThroughput": -1,
                                     "leaseCollectionPrefix": None,
                                     "checkpointInterval": -1,
                                     "checkpointDocumentCount": -1,
                                     "feedPollDelay": 5000,
                                     "leaseRenewInterval": 17000,
                                     "leaseAcquireInterval": 13000,
                                     "leaseExpirationInterval": 60000,
                                     "maxItemsPerInvocation": -1,
                                     "startFromBeginning": False,
                                     "preferredLocations": "",
                                     "connectionStringSetting": "dummy_str",
                                     "databaseName": "dummy_db",
                                     "collectionName": "dummy_collection"
                                 }
                             ]
                         }))

    def test_multiple_triggers(self):
        app = self.func_app
        with self.assertRaises(ValueError) as err:
            trigger1 = TimerTrigger(name="req1", schedule="dummy_schedule",
                                    run_on_startup=False, use_monitor=False,
                                    data_type=DataType.UNDEFINED)
            trigger2 = TimerTrigger(name="req2", schedule="dummy_schedule",
                                    run_on_startup=False, use_monitor=False,
                                    data_type=DataType.UNDEFINED)

            @app.schedule(arg_name="req1", schedule="dummy_schedule")
            @app.schedule(arg_name="req2", schedule="dummy_schedule")
            def dummy():
                pass

        self.assertEqual(err.exception.args[0],
                         "A trigger was already registered to this "
                         "function. Adding another trigger is not the "
                         "correct behavior as a function can only have one "
                         "trigger. Existing registered trigger "
                         f"is {trigger2} and New trigger "
                         f"being added is {trigger1}")

    def test_no_trigger(self):
        app = self.func_app
        with self.assertRaises(ValueError) as err:
            @app.write_queue(arg_name="out", queue_name="dummy_out_queue",
                             connection="dummy_out_conn")
            def dummy():
                pass

            app.get_functions()

        self.assertEqual(err.exception.args[0],
                         "Function dummy does not have a trigger")

    def test_multiple_input_bindings(self):
        app = self.func_app

        @app.schedule(arg_name="req1", schedule="dummy_schedule")
        @app.read_cosmos_db_documents(
            arg_name="in1",
            database_name="dummy_in_db",
            collection_name="dummy_in_collection",
            connection_string_setting="dummy_str",
            document_id="dummy_id",
            sql_query="dummy_query",
            partition_key="dummy_partitions",
            data_type=DataType.STRING)
        @app.read_cosmos_db_documents(
            arg_name="in2",
            database_name="dummy_in_db",
            collection_name="dummy_in_collection",
            connection_string_setting="dummy_str",
            document_id="dummy_id",
            sql_query="dummy_query",
            partition_key="dummy_partitions",
            data_type=DataType.STRING)
        @app.write_queue(arg_name="out1", queue_name="dummy_out_queue",
                         connection="dummy_out_conn")
        @app.write_event_hub_message(
            arg_name="res",
            event_hub_name="dummy_event_hub",
            connection="dummy_connection")
        def dummy():
            pass

        func = self._get_func(app)

        self.assertEqual(str(func),
                         json.dumps({
                             "scriptFile": "function_app.py",
                             "bindings": [
                                 {
                                     "type": "eventHub",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "res",
                                     "dataType": str(DataType.UNDEFINED),
                                     "connection": "dummy_connection",
                                     "eventHubName": "dummy_event_hub"
                                 },
                                 {
                                     "type": "queue",
                                     "direction": str(BindingDirection.OUT),
                                     "name": "out1",
                                     "dataType": str(DataType.UNDEFINED),
                                     "queueName": "dummy_out_queue",
                                     "connection": "dummy_out_conn"
                                 },
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.IN),
                                     "name": "in2",
                                     "dataType": str(DataType.STRING),
                                     "databaseName": "dummy_in_db",
                                     "collectionName": "dummy_in_collection",
                                     "collectionStringSetting": "dummy_str",
                                     "document_id": "dummy_id",
                                     "sqlQuery": "dummy_query",
                                     "partitionKey": "dummy_partitions"
                                 },
                                 {
                                     "type": "cosmosDB",
                                     "direction": str(BindingDirection.IN),
                                     "name": "in1",
                                     "dataType": str(DataType.STRING),
                                     "databaseName": "dummy_in_db",
                                     "collectionName": "dummy_in_collection",
                                     "collectionStringSetting": "dummy_str",
                                     "document_id": "dummy_id",
                                     "sqlQuery": "dummy_query",
                                     "partitionKey": "dummy_partitions"
                                 },
                                 {
                                     "name": "req1",
                                     "type": "timerTrigger",
                                     "dataType": str(DataType.UNDEFINED),
                                     "direction": str(BindingDirection.IN),
                                     "schedule": "dummy_schedule",
                                     "runOnStartup": False,
                                     "useMonitor": False
                                 }
                             ]
                         }))

    def test_set_auth_level_for_http_functions(self):
        app = FunctionsApp(auth_level=AuthLevel.ANONYMOUS)

        @app.route(auth_level=AuthLevel.ADMIN)
        def specify_auth_level():
            pass

        @app.route()
        def default_auth_level():
            pass

        funcs = app.get_functions()
        self.assertEqual(len(funcs), 2)
        http_func_1 = funcs[0]
        http_func_2 = funcs[1]

        self.assertEqual(http_func_1.get_user_function().__name__,
                         "specify_auth_level")
        self.assertEqual(http_func_2.get_user_function().__name__,
                         "default_auth_level")

        self.assertEqual(str(http_func_1), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "authLevel": "admin",
                    "type": "httpTrigger",
                    "direction": str(BindingDirection.IN),
                    "name": "req",
                    "dataType": str(DataType.UNDEFINED),
                    "route": "specify_auth_level",
                    "methods": [
                        "GET", "POST"
                    ]
                },
                {
                    "type": "http",
                    "direction": str(BindingDirection.OUT),
                    "name": "$return",
                    "dataType": str(DataType.UNDEFINED)
                }
            ]
        }))

        self.assertEqual(str(http_func_2), json.dumps({
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "authLevel": "anonymous",
                    "type": "httpTrigger",
                    "direction": str(BindingDirection.IN),
                    "name": "req",
                    "dataType": str(DataType.UNDEFINED),
                    "route": "default_auth_level",
                    "methods": [
                        "GET", "POST"
                    ]
                },
                {
                    "type": "http",
                    "direction": str(BindingDirection.OUT),
                    "name": "$return",
                    "dataType": str(DataType.UNDEFINED)
                }
            ]
        }))

    def _get_func(self, app):
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        func = funcs[0]
        return func
