#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.blob import BlobTrigger, BlobOutput, BlobInput
from azure.functions.decorators.core import BindingDirection, BlobSource, \
    DataType


class TestBlob(unittest.TestCase):
    def test_blob_trigger_creation_with_no_source(self):
        trigger = BlobTrigger(name="req",
                              path="dummy_path",
                              connection="dummy_connection",
                              data_type=DataType.UNDEFINED,
                              dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "blobTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "blobTrigger",
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            "connection": "dummy_connection"
        })

    def test_blob_trigger_creation_with_default_specified_source(self):
        trigger = BlobTrigger(name="req",
                              path="dummy_path",
                              connection="dummy_connection",
                              source=BlobSource.LOGS_AND_CONTAINER_SCAN,
                              data_type=DataType.UNDEFINED,
                              dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "blobTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "blobTrigger",
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            'source': 'LogsAndContainerScan',
            "connection": "dummy_connection"
        })

    def test_blob_trigger_creation_with_source_as_string(self):
        trigger = BlobTrigger(name="req",
                              path="dummy_path",
                              connection="dummy_connection",
                              source="EventGrid",
                              data_type=DataType.UNDEFINED,
                              dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "blobTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "blobTrigger",
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            'source': 'EventGrid',
            "connection": "dummy_connection"
        })

    def test_blob_trigger_creation_with_source_as_enum(self):
        trigger = BlobTrigger(name="req",
                              path="dummy_path",
                              connection="dummy_connection",
                              source=BlobSource.EVENT_GRID,
                              data_type=DataType.UNDEFINED,
                              dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "blobTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "blobTrigger",
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            'source': 'EventGrid',
            "connection": "dummy_connection"
        })

    def test_blob_input_valid_creation(self):
        blob_input = BlobInput(name="res",
                               path="dummy_path",
                               connection="dummy_connection",
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(blob_input.get_binding_name(), "blob")
        self.assertEqual(blob_input.get_dict_repr(), {
            "type": "blob",
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            "connection": "dummy_connection"
        })

    def test_blob_output_valid_creation(self):
        blob_output = BlobOutput(name="res",
                                 path="dummy_path",
                                 connection="dummy_connection",
                                 data_type=DataType.UNDEFINED,
                                 dummy_field="dummy")

        self.assertEqual(blob_output.get_binding_name(), "blob")
        self.assertEqual(blob_output.get_dict_repr(), {
            "type": "blob",
            "direction": BindingDirection.OUT,
            'dummyField': 'dummy',
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "path": "dummy_path",
            "connection": "dummy_connection"
        })
