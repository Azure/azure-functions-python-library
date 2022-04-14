#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import TIMER_TRIGGER, HTTP_TRIGGER, \
    HTTP_OUTPUT, QUEUE, QUEUE_TRIGGER, SERVICE_BUS, SERVICE_BUS_TRIGGER, \
    EVENT_HUB, EVENT_HUB_TRIGGER, COSMOS_DB, COSMOS_DB_TRIGGER, BLOB, \
    BLOB_TRIGGER
from azure.functions.decorators.core import DataType, AuthLevel, \
    BindingDirection, AccessRights, Cardinality
from azure.functions.decorators.function_app import FunctionApp
from azure.functions.decorators.http import HttpTrigger, HttpMethod
from azure.functions.decorators.timer import TimerTrigger
from tests.decorators.testutils import assert_json


class TestFunctionsApp(unittest.TestCase):
    def setUp(self):
        self.func_app = FunctionApp()

    def _get_func(self, app):
        funcs = app.get_functions()
        self.assertEqual(len(funcs), 1)
        return funcs[0]

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
        @app.route("dummy")
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
        assert_json(self, func, {
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "name": "req",
                    "type": TIMER_TRIGGER,
                    "direction": BindingDirection.IN,
                    "schedule": "dummy_schedule"
                }
            ]
        })

    def test_timer_trigger_full_args(self):
        app = self.func_app

        @app.schedule(arg_name="req", schedule="dummy_schedule",
                      run_on_startup=False, use_monitor=False,
                      data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)
        assert_json(self, func, {
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "name": "req",
                    "type": TIMER_TRIGGER,
                    "dataType": DataType.STRING,
                    "direction": BindingDirection.IN,
                    "schedule": "dummy_schedule",
                    "runOnStartup": False,
                    "useMonitor": False
                }
            ]
        })

    def test_route_default_args(self):
        app = self.func_app

        @app.route()
        def dummy():
            pass

        func = self._get_func(app)
        assert_json(self, func, {
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "direction": BindingDirection.IN,
                    "type": HTTP_TRIGGER,
                    "name": "req",
                    "authLevel": AuthLevel.FUNCTION,
                    "route": "dummy"
                },
                {
                    "direction": BindingDirection.OUT,
                    "type": HTTP_OUTPUT,
                    "name": "$return"
                }
            ]
        })

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
        assert_json(self, func, {
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "direction": BindingDirection.IN,
                    "type": HTTP_TRIGGER,
                    "dataType": DataType.STRING,
                    "name": "trigger_name",
                    "authLevel": AuthLevel.FUNCTION,
                    "route": "dummy_route",
                    "methods": [
                        "GET", "PATCH"
                    ]
                },
                {
                    "direction": BindingDirection.OUT,
                    "dataType": DataType.STRING,
                    "type": HTTP_OUTPUT,
                    "name": "out",
                }
            ]
        })

    def test_queue_default_args(self):
        app = self.func_app

        @app.on_queue_change(arg_name="req", queue_name="dummy_queue",
                             connection="dummy_conn")
        @app.write_queue(arg_name="out", queue_name="dummy_out_queue",
                         connection="dummy_out_conn")
        def dummy():
            pass

        func = self._get_func(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": QUEUE,
                                         "name": "out",
                                         "queueName": "dummy_out_queue",
                                         "connection": "dummy_out_conn"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": QUEUE_TRIGGER,
                                         "name": "req",
                                         "queueName": "dummy_queue",
                                         "connection": "dummy_conn"
                                     }]})

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "dataType": DataType.STRING,
                                         "type": QUEUE,
                                         "name": "out",
                                         "queueName": "dummy_out_queue",
                                         "connection": "dummy_out_conn"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STRING,
                                         "type": QUEUE_TRIGGER,
                                         "name": "req",
                                         "queueName": "dummy_queue",
                                         "connection": "dummy_conn"
                                     }]})

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": SERVICE_BUS,
                                         "name": "res",
                                         "connection": "dummy_out_conn",
                                         "queueName": "dummy_out_queue"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": SERVICE_BUS_TRIGGER,
                                         "name": "req",
                                         "connection": "dummy_conn",
                                         "queueName": "dummy_queue"
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "dataType": DataType.STREAM,
                                         "type": SERVICE_BUS,
                                         "name": "res",
                                         "connection": "dummy_out_conn",
                                         "queueName": "dummy_out_queue",
                                         "accessRights": AccessRights.MANAGE
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STREAM,
                                         "type": SERVICE_BUS_TRIGGER,
                                         "name": "req",
                                         "connection": "dummy_conn",
                                         "queueName": "dummy_queue",
                                         "accessRights": AccessRights.MANAGE,
                                         "isSessionsEnabled": True,
                                         "cardinality": Cardinality.MANY
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "type": SERVICE_BUS,
                                         "direction": BindingDirection.OUT,
                                         "name": "res",
                                         "connection": "dummy_conn",
                                         "topicName": "dummy_topic",
                                         "subscriptionName": "dummy_sub"
                                     },
                                     {
                                         "type": SERVICE_BUS_TRIGGER,
                                         "direction": BindingDirection.IN,
                                         "name": "req",
                                         "connection": "dummy_conn",
                                         "topicName": "dummy_topic",
                                         "subscriptionName": "dummy_sub"
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "type": SERVICE_BUS,
                                         "direction": BindingDirection.OUT,
                                         "name": "res",
                                         "connection": "dummy_conn",
                                         "topicName": "dummy_topic",
                                         "subscriptionName": "dummy_sub",
                                         "dataType": DataType.STRING,
                                         "accessRights": AccessRights.LISTEN
                                     },
                                     {
                                         "type": SERVICE_BUS_TRIGGER,
                                         "direction": BindingDirection.IN,
                                         "name": "req",
                                         "connection": "dummy_conn",
                                         "topicName": "dummy_topic",
                                         "subscriptionName": "dummy_sub",
                                         "dataType": DataType.STRING,
                                         "accessRights": AccessRights.LISTEN,
                                         "isSessionsEnabled": False,
                                         "cardinality": Cardinality.MANY
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": EVENT_HUB,
                                         "name": "res",
                                         "connection": "dummy_connection",
                                         "eventHubName": "dummy_event_hub"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": EVENT_HUB_TRIGGER,
                                         "name": "req",
                                         "connection": "dummy_connection",
                                         "eventHubName": "dummy_event_hub"
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {
            "scriptFile": "function_app.py",
            "bindings": [
                {
                    "direction": BindingDirection.OUT,
                    "dataType": DataType.UNDEFINED,
                    "type": EVENT_HUB,
                    "name": "res",
                    "connection": "dummy_connection",
                    "eventHubName": "dummy_event_hub"
                },
                {
                    "direction": BindingDirection.IN,
                    "dataType": DataType.UNDEFINED,
                    "type": EVENT_HUB_TRIGGER,
                    "name": "req",
                    "connection": "dummy_connection",
                    "eventHubName": "dummy_event_hub",
                    "cardinality": Cardinality.ONE,
                    "consumerGroup": "dummy_group"
                }
            ]
        })

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
                                      id="dummy_id",
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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "dataType": DataType.STRING,
                                         "type": COSMOS_DB,
                                         "name": "out",
                                         "databaseName": "dummy_out_db",
                                         "collectionName":
                                             "dummy_out_collection",
                                         "connectionStringSetting":
                                             "dummy_str",
                                         "createIfNotExists": False,
                                         "collectionThroughput": 1,
                                         "useMultipleWriteLocations": False,
                                         "preferredLocations":
                                             "dummy_location",
                                         "partitionKey": "dummy_part_key"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STRING,
                                         "type": COSMOS_DB,
                                         "name": "in",
                                         "databaseName": "dummy_in_db",
                                         "collectionName":
                                             "dummy_in_collection",
                                         "connectionStringSetting":
                                             "dummy_str",
                                         "id": "dummy_id",
                                         "sqlQuery": "dummy_query",
                                         "partitionKey": "dummy_partitions"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STRING,
                                         "type": COSMOS_DB_TRIGGER,
                                         "name": "trigger",
                                         "databaseName": "dummy_db",
                                         "collectionName": "dummy_collection",
                                         "connectionStringSetting":
                                             "dummy_str",
                                         "leasesCollectionThroughput": 1,
                                         "checkpointInterval": 2,
                                         "checkpointDocumentCount": 3,
                                         "feedPollDelay": 4,
                                         "leaseRenewInterval": 5,
                                         "leaseAcquireInterval": 6,
                                         "leaseExpirationInterval": 7,
                                         "maxItemsPerInvocation": 8,
                                         "startFromBeginning": False,
                                         "createLeaseCollectionIfNotExists":
                                             False,
                                         "preferredLocations": "dummy_loc",
                                         "leaseCollectionName":
                                             "dummy_lease_col",
                                         "leaseConnectionStringSetting":
                                             "dummy_lease_conn_str",
                                         "leaseDatabaseName": "dummy_lease_db",
                                         "leaseCollectionPrefix":
                                             "dummy_lease_collection_prefix"
                                     }
                                 ]
                                 })

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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": COSMOS_DB,
                                         "name": "out",
                                         "databaseName": "dummy_out_db",
                                         "collectionName":
                                             "dummy_out_collection",
                                         "connectionStringSetting": "dummy_str"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": COSMOS_DB,
                                         "name": "in",
                                         "databaseName": "dummy_in_db",
                                         "collectionName":
                                             "dummy_in_collection",
                                         "connectionStringSetting": "dummy_str"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": COSMOS_DB_TRIGGER,
                                         "name": "trigger",
                                         "databaseName": "dummy_db",
                                         "collectionName": "dummy_collection",
                                         "connectionStringSetting": "dummy_str"
                                     }
                                 ]
                                 })

    def test_multiple_triggers(self):
        app = self.func_app
        with self.assertRaises(ValueError) as err:
            trigger1 = TimerTrigger(name="req1", schedule="dummy_schedule")
            trigger2 = TimerTrigger(name="req2", schedule="dummy_schedule")

            @app.schedule(arg_name="req1", schedule="dummy_schedule")
            @app.schedule(arg_name="req2", schedule="dummy_schedule")
            def dummy():
                pass
        self.assertEqual(err.exception.args[0],
                         "A trigger was already registered to this "
                         "function. Adding another trigger is not the "
                         "correct behavior as a function can only have one "
                         "trigger. Existing registered trigger "
                         f"is {trigger2.get_dict_repr()} and New trigger "
                         f"being added is {trigger1.get_dict_repr()}")

    def test_no_trigger(self):
        app = self.func_app
        with self.assertRaises(ValueError) as err:
            @app.write_queue(arg_name="out", queue_name="dummy_out_queue",
                             connection="dummy_out_conn")
            def dummy():
                pass

            app.get_functions()

        self.assertEqual(err.exception.args[0],
                         "Function dummy does not have a trigger. A valid "
                         "function must have one and only one trigger "
                         "registered.")

    def test_multiple_input_bindings(self):
        app = self.func_app

        @app.schedule(arg_name="req1", schedule="dummy_schedule")
        @app.read_cosmos_db_documents(
            arg_name="in1",
            database_name="dummy_in_db",
            collection_name="dummy_in_collection",
            connection_string_setting="dummy_str",
            id="dummy_id",
            sql_query="dummy_query",
            partition_key="dummy_partitions",
            data_type=DataType.STRING)
        @app.read_cosmos_db_documents(
            arg_name="in2",
            database_name="dummy_in_db",
            collection_name="dummy_in_collection",
            connection_string_setting="dummy_str",
            id="dummy_id",
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

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": EVENT_HUB,
                                         "name": "res",
                                         "connection": "dummy_connection",
                                         "eventHubName": "dummy_event_hub"
                                     },
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": QUEUE,
                                         "name": "out1",
                                         "queueName": "dummy_out_queue",
                                         "connection": "dummy_out_conn"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STRING,
                                         "type": COSMOS_DB,
                                         "name": "in2",
                                         "databaseName": "dummy_in_db",
                                         "collectionName":
                                             "dummy_in_collection",
                                         "connectionStringSetting":
                                             "dummy_str",
                                         "id": "dummy_id",
                                         "sqlQuery": "dummy_query",
                                         "partitionKey": "dummy_partitions"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "dataType": DataType.STRING,
                                         "type": COSMOS_DB,
                                         "name": "in1",
                                         "databaseName": "dummy_in_db",
                                         "collectionName":
                                             "dummy_in_collection",
                                         "connectionStringSetting":
                                             "dummy_str",
                                         "id": "dummy_id",
                                         "sqlQuery": "dummy_query",
                                         "partitionKey": "dummy_partitions"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": TIMER_TRIGGER,
                                         "name": "req1",
                                         "schedule": "dummy_schedule"
                                     }
                                 ]
                                 })

    def test_set_auth_level_for_http_functions(self):
        app = FunctionApp(auth_level=AuthLevel.ANONYMOUS)

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

        assert_json(self, http_func_1, {"scriptFile": "function_app.py",
                                        "bindings": [
                                            {
                                                "authLevel": AuthLevel.ADMIN,
                                                "type": HTTP_TRIGGER,
                                                "direction":
                                                    BindingDirection.IN,
                                                "name": "req",
                                                "route": "specify_auth_level"
                                            },
                                            {
                                                "type": HTTP_OUTPUT,
                                                "direction":
                                                    BindingDirection.OUT,
                                                "name": "$return"
                                            }
                                        ]
                                        })

        assert_json(self, http_func_2, {"scriptFile": "function_app.py",
                                        "bindings": [
                                            {
                                                "authLevel":
                                                    AuthLevel.ANONYMOUS,
                                                "type": HTTP_TRIGGER,
                                                "direction":
                                                    BindingDirection.IN,
                                                "name": "req",
                                                "route": "default_auth_level"
                                            },
                                            {
                                                "type": HTTP_OUTPUT,
                                                "direction":
                                                    BindingDirection.OUT,
                                                "name": "$return"
                                            }
                                        ]
                                        })

    def test_blob_default_args(self):
        app = self.func_app

        @app.on_blob_change(arg_name="req", path="dummy_path",
                            connection="dummy_conn")
        @app.read_blob(arg_name="file", path="dummy_path",
                       connection="dummy_conn")
        @app.write_blob(arg_name="out", path="dummy_out_path",
                        connection="dummy_out_conn")
        def dummy():
            pass

        func = self._get_func(app)

        assert_json(self, func, {"scriptFile": "function_app.py",
                                 "bindings": [
                                     {
                                         "direction": BindingDirection.OUT,
                                         "type": BLOB,
                                         "name": "out",
                                         "path": "dummy_out_path",
                                         "connection": "dummy_out_conn"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": BLOB,
                                         "name": "file",
                                         "path": "dummy_path",
                                         "connection": "dummy_conn"
                                     },
                                     {
                                         "direction": BindingDirection.IN,
                                         "type": BLOB_TRIGGER,
                                         "name": "req",
                                         "path": "dummy_path",
                                         "connection": "dummy_conn"
                                     }]})

    def test_blob_trigger(self):
        app = self.func_app

        @app.on_blob_change(arg_name="req", path="dummy_path",
                            data_type=DataType.STRING,
                            connection="dummy_conn")
        def dummy():
            pass

        func = self._get_func(app)

        trigger = func.get_bindings()[0]

        self.assertEqual(trigger.get_dict_repr(), {
            "direction": BindingDirection.IN,
            "dataType": DataType.STRING,
            "type": BLOB_TRIGGER,
            "name": "req",
            "path": "dummy_path",
            "connection": "dummy_conn"
        })

    def test_blob_input_binding(self):
        app = self.func_app

        @app.on_blob_change(arg_name="req", path="dummy_path",
                            data_type=DataType.STRING,
                            connection="dummy_conn")
        @app.read_blob(arg_name="file", path="dummy_in_path",
                       connection="dummy_in_conn",
                       data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)

        trigger = func.get_bindings()[0]

        self.assertEqual(trigger.get_dict_repr(), {
            "direction": BindingDirection.IN,
            "dataType": DataType.STRING,
            "type": BLOB,
            "name": "file",
            "path": "dummy_in_path",
            "connection": "dummy_in_conn"
        })

    def test_blob_output_binding(self):
        app = self.func_app

        @app.on_blob_change(arg_name="req", path="dummy_path",
                            data_type=DataType.STRING,
                            connection="dummy_conn")
        @app.write_blob(arg_name="out", path="dummy_out_path",
                        connection="dummy_out_conn",
                        data_type=DataType.STRING)
        def dummy():
            pass

        func = self._get_func(app)

        trigger = func.get_bindings()[0]

        self.assertEqual(trigger.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "dataType": DataType.STRING,
            "type": BLOB,
            "name": "out",
            "path": "dummy_out_path",
            "connection": "dummy_out_conn"
        })
