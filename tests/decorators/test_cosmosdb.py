#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.cosmosdb import CosmosDBTrigger, \
    CosmosDBOutput, CosmosDBInput


class TestCosmosDB(unittest.TestCase):
    def test_cosmos_db_trigger_valid_creation(self):
        trigger = CosmosDBTrigger(name="req", database_name="dummy_db",
                                  collection_name="dummy_collection",
                                  connection_string_setting="dummy_str",
                                  leases_collection_throughput=1,
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
                                  data_type=DataType.UNDEFINED)

        self.assertEqual(trigger.get_binding_name(), "cosmosDBTrigger")
        self.assertEqual(trigger.get_dict_repr(), {"checkpointDocumentCount": 3,
                                                   "checkpointInterval": 2,
                                                   "collectionName":
                                                       "dummy_collection",
                                                   "connectionStringSetting":
                                                       "dummy_str",
                                                   "createLeaseCollection"
                                                   "IfNotExists":
                                                       False,
                                                   "dataType":
                                                       DataType.UNDEFINED.value,
                                                   "databaseName": "dummy_db",
                                                   "direction": BindingDirection
                                                                .IN.value,
                                                   "feedPollDelay": 4,
                                                   "leaseAcquireInterval": 6,
                                                   "leaseCollectionName": None,
                                                   "leaseCollectionPrefix":
                                                       None,
                                                   "leaseConnection"
                                                   "StringSetting":
                                                       None,
                                                   "leaseDatabaseName": None,
                                                   "leaseExpirationInterval": 7,
                                                   "leaseRenewInterval": 5,
                                                   "leasesCollectionThroughput":
                                                       1,
                                                   "maxItemsPerInvocation": 8,
                                                   "name": "req",
                                                   "preferredLocations":
                                                       "dummy_loc",
                                                   "startFromBeginning": False,
                                                   "type": "cosmosDBTrigger"})

    def test_cosmos_db_output_valid_creation(self):
        output = CosmosDBOutput(name="req", database_name="dummy_db",
                                collection_name="dummy_collection",
                                connection_string_setting="dummy_str",
                                create_if_not_exists=False,
                                collection_throughput=1,
                                use_multiple_write_locations=False)

        self.assertEqual(output.get_binding_name(), "cosmosDB")
        self.assertEqual(output.get_dict_repr(),
                         {'collectionName': 'dummy_collection',
                          'collectionThroughput': 1,
                          'connectionStringSetting': 'dummy_str',
                          'createIfNotExists': False,
                          'dataType': DataType.UNDEFINED.value,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.OUT.value,
                          'name': 'req',
                          'partitionKey': None,
                          'preferredLocations': None,
                          'type': 'cosmosDB',
                          'useMultipleWriteLocations': False})

    def test_cosmos_db_input_valid_creation(self):
        cosmosdb_input = CosmosDBInput(name="req", database_name="dummy_db",
                                       collection_name="dummy_collection",
                                       connection_string_setting="dummy_str",
                                       document_id="dummy_id", sql_query=
                                       "dummy_query",
                                       partition_key="dummy_partitions",
                                       data_type=DataType.UNDEFINED)
        self.assertEqual(cosmosdb_input.get_binding_name(), "cosmosDB")
        self.assertEqual(cosmosdb_input.get_dict_repr(),
                         {'collectionName': 'dummy_collection',
                          'collectionStringSetting': 'dummy_str',
                          'dataType': DataType.UNDEFINED.value,
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.IN.value,
                          'document_id': 'dummy_id',
                          'name': 'req',
                          'partitionKey': 'dummy_partitions',
                          'sqlQuery': 'dummy_query',
                          'type': 'cosmosDB'})
