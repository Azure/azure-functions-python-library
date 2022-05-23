#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import HTTP_TRIGGER, COSMOS_DB, BLOB
from azure.functions.decorators.core import BindingDirection, AuthLevel, \
    DataType
from azure.functions.decorators.generic import GenericInputBinding, \
    GenericTrigger, GenericOutputBinding


class TestGeneric(unittest.TestCase):
    def test_generic_trigger_valid_creation(self):
        trigger = GenericTrigger(name="req",
                                 type=HTTP_TRIGGER,
                                 data_type=DataType.UNDEFINED,
                                 auth_level=AuthLevel.ANONYMOUS,
                                 methods=["GET", "POST"],
                                 route="dummy")

        self.assertEqual(trigger.get_binding_name(), None)
        self.assertEqual(trigger.type, HTTP_TRIGGER)
        self.assertEqual(trigger.get_dict_repr(), {
            "authLevel": AuthLevel.ANONYMOUS,
            "type": HTTP_TRIGGER,
            "direction": BindingDirection.IN,
            "name": 'req',
            "dataType": DataType.UNDEFINED,
            "route": 'dummy',
            "methods": ["GET", "POST"]
        })

    def test_generic_input_valid_creation(self):
        cosmosdb_input = GenericInputBinding(
            name="inDocs",
            type=COSMOS_DB,
            database_name="dummy_db",
            collection_name="dummy_collection",
            connection_string_setting="dummy_str",
            id='dummy_id',
            partitionKey='dummy_partitions',
            sqlQuery='dummy_query')
        self.assertEqual(cosmosdb_input.get_binding_name(), None)
        self.assertEqual(cosmosdb_input.get_dict_repr(),
                         {'collectionName': 'dummy_collection',
                          'connectionStringSetting': 'dummy_str',
                          'databaseName': 'dummy_db',
                          'direction': BindingDirection.IN,
                          'id': 'dummy_id',
                          'name': 'inDocs',
                          'partitionKey': 'dummy_partitions',
                          'sqlQuery': 'dummy_query',
                          'type': COSMOS_DB})

    def test_generic_output_valid_creation(self):
        blob_output = GenericOutputBinding(name="res", type=BLOB,
                                           data_type=DataType.UNDEFINED,
                                           path="dummy_path",
                                           connection="dummy_connection")

        self.assertEqual(blob_output.get_binding_name(), None)
        self.assertEqual(blob_output.get_dict_repr(), {
            "type": BLOB,
            "direction": BindingDirection.OUT,
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            "connection": "dummy_connection"
        })
