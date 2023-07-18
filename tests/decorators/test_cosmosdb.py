#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import COSMOS_DB_TRIGGER, COSMOS_DB
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput, CosmosDBTriggerV3, CosmosDBOutputV3, \
    CosmosDBInputV3


class TestCosmosDB(unittest.TestCase):
    def test_cosmos_db_trigger_v3_valid_creation(self):
        trigger = CosmosDBTriggerV3(name="req", database_name="dummy_db",
                                    collection_name="dummy_collection",
                                    connection_string_setting="dummy_str",
                                    leases_collection_throughput=1,
                                    checkpoint_interval=2,
                                    checkpoint_document_count=3,
                                    feed_poll_delay=4,
                                    lease_renew_interval=5,
                                    lease_acquire_interval=6,
                                    lease_expiration_interval=7,
                                    lease_collection_name='coll_name',
                                    lease_collection_prefix='prefix',
                                    lease_connection_string_setting='setting',
                                    lease_database_name='db',
                                    max_items_per_invocation=8,
                                    start_from_beginning=False,
                                    create_lease_collection_if_not_exists=False,  # NoQA
                                    preferred_locations="dummy_loc",
                                    data_type=DataType.UNDEFINED,
                                    dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "cosmosDBTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"checkpointDocumentCount": 3,
                          "checkpointInterval": 2,
                          "collectionName": "dummy_collection",
                          "connectionStringSetting": "dummy_str",
                          "createLeaseCollectionIfNotExists": False,
                          "dataType": DataType.UNDEFINED,
                          "databaseName": "dummy_db",
                          "direction": BindingDirection.IN,
                          'dummyField': 'dummy',
                          "feedPollDelay": 4,
                          "leaseAcquireInterval": 6,
                          "leaseCollectionName": 'coll_name',
                          "leaseCollectionPrefix": 'prefix',
                          "leaseConnectionStringSetting": 'setting',
                          "leaseDatabaseName": 'db',
                          "leaseExpirationInterval": 7,
                          "leaseRenewInterval": 5,
                          "leasesCollectionThroughput": 1,
                          "maxItemsPerInvocation": 8,
                          "name": "req",
                          "preferredLocations": "dummy_loc",
                          "startFromBeginning": False,
                          "type": COSMOS_DB_TRIGGER})

    def test_cosmos_db_output_v3_valid_creation(self):
        output = CosmosDBOutputV3(name="req",
                                  database_name="dummy_db",
                                  collection_name="dummy_collection",
                                  connection_string_setting="dummy_str",
                                  create_if_not_exists=False,
                                  collection_throughput=1,
                                  use_multiple_write_locations=False,
                                  data_type=DataType.UNDEFINED,
                                  partition_key='key',
                                  preferred_locations='locs',
                                  dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "cosmosDB")
        self.assertEqual(output.get_dict_repr(),
                         {'collectionName': 'dummy_collection',
                          'collectionThroughput': 1,
                          'connectionStringSetting': 'dummy_str',
                          'createIfNotExists': False,
                          'dataType': DataType.UNDEFINED,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.OUT,
                          'dummyField': 'dummy',
                          'name': 'req',
                          'partitionKey': 'key',
                          'preferredLocations': 'locs',
                          'type': COSMOS_DB,
                          'useMultipleWriteLocations': False})

    def test_cosmos_db_input_v3_valid_creation(self):
        cosmosdb_input = CosmosDBInputV3(name="req", database_name="dummy_db",
                                         collection_name="dummy_collection",
                                         connection_string_setting="dummy_str",
                                         id="dummy_id",
                                         sql_query="dummy_query",
                                         partition_key="dummy_partitions",
                                         data_type=DataType.UNDEFINED,
                                         dummy_field="dummy")
        self.assertEqual(cosmosdb_input.get_binding_name(), "cosmosDB")
        self.assertEqual(cosmosdb_input.get_dict_repr(),
                         {'collectionName': 'dummy_collection',
                          'connectionStringSetting': 'dummy_str',
                          'dataType': DataType.UNDEFINED,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.IN,
                          'dummyField': 'dummy',
                          'id': 'dummy_id',
                          'name': 'req',
                          'partitionKey': 'dummy_partitions',
                          'sqlQuery': 'dummy_query',
                          'type': COSMOS_DB})

    def test_cosmos_db_trigger_valid_creation(self):
        trigger = CosmosDBTrigger(name="req", database_name="dummy_db",
                                  container_name="dummy_container",
                                  connection="dummy_str",
                                  leases_container_throughput=1,
                                  feed_poll_delay=4,
                                  lease_renew_interval=5,
                                  lease_acquire_interval=6,
                                  lease_expiration_interval=7,
                                  lease_container_name='container_name',
                                  lease_container_prefix='prefix',
                                  lease_connection='setting',
                                  lease_database_name='db',
                                  max_items_per_invocation=8,
                                  start_from_beginning=False,
                                  start_from_time="2021-02-16T14:19:29Z",
                                  create_lease_container_if_not_exists=False,
                                  preferred_locations="dummy_loc",
                                  data_type=DataType.UNDEFINED,
                                  dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "cosmosDBTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"containerName": "dummy_container",
                          "connection": "dummy_str",
                          "createLeaseContainerIfNotExists": False,
                          "dataType": DataType.UNDEFINED,
                          "databaseName": "dummy_db",
                          "direction": BindingDirection.IN,
                          'dummyField': 'dummy',
                          "feedPollDelay": 4,
                          "leaseAcquireInterval": 6,
                          "leaseContainerName": 'container_name',
                          "leaseContainerPrefix": 'prefix',
                          "leaseConnection": 'setting',
                          "leaseDatabaseName": 'db',
                          "leaseExpirationInterval": 7,
                          "leaseRenewInterval": 5,
                          "leasesContainerThroughput": 1,
                          "maxItemsPerInvocation": 8,
                          "name": "req",
                          "preferredLocations": "dummy_loc",
                          "startFromBeginning": False,
                          "startFromTime": "2021-02-16T14:19:29Z",
                          "type": COSMOS_DB_TRIGGER})

    def test_cosmos_db_output_valid_creation(self):
        output = CosmosDBOutput(name="req",
                                database_name="dummy_db",
                                container_name="dummy_container",
                                connection="dummy_str",
                                create_if_not_exists=False,
                                container_throughput=1,
                                use_multiple_write_locations=False,
                                data_type=DataType.UNDEFINED,
                                partition_key='key',
                                preferred_locations='locs',
                                dummy_field="dummy")
        self.assertEqual(output.get_binding_name(), "cosmosDB")
        self.assertEqual(output.get_dict_repr(),
                         {'containerName': 'dummy_container',
                          'containerThroughput': 1,
                          'connection': 'dummy_str',
                          'createIfNotExists': False,
                          'dataType': DataType.UNDEFINED,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.OUT,
                          'dummyField': 'dummy',
                          'name': 'req',
                          'partitionKey': 'key',
                          'preferredLocations': 'locs',
                          'type': COSMOS_DB,
                          'useMultipleWriteLocations': False})

    def test_cosmos_db_input_valid_creation(self):
        cosmosdb_input = CosmosDBInput(name="req",
                                       database_name="dummy_db",
                                       container_name="dummy_container",
                                       connection="dummy_str",
                                       id="dummy_id",
                                       sql_query="dummy_query",
                                       partition_key="dummy_partitions",
                                       preferred_locations="EastUS",
                                       data_type=DataType.UNDEFINED,
                                       dummy_field="dummy")
        self.assertEqual(cosmosdb_input.get_binding_name(), "cosmosDB")
        self.assertEqual(cosmosdb_input.get_dict_repr(),
                         {'containerName': 'dummy_container',
                          'connection': 'dummy_str',
                          'dataType': DataType.UNDEFINED,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.IN,
                          'dummyField': 'dummy',
                          'id': 'dummy_id',
                          'name': 'req',
                          'partitionKey': 'dummy_partitions',
                          'sqlQuery': 'dummy_query',
                          'preferredLocations': "EastUS",
                          'type': COSMOS_DB})
