#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions import DataType
from azure.functions.decorators.core import BindingDirection
from azure.functions.decorators.queue import QueueTrigger, QueueOutput


class TestQueue(unittest.TestCase):
    def test_queue_trigger_valid_creation(self):
        trigger = QueueTrigger(name="req",
                               queue_name="dummy_queue",
                               connection="dummy_connection",
                               data_type=DataType.UNDEFINED)

        self.assertEqual(trigger.get_binding_name(), "queueTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": "queueTrigger",
            "direction": str(BindingDirection.IN),
            "name": "req",
            "dataType": str(DataType.UNDEFINED),
            "queueName": "dummy_queue",
            "connection": "dummy_connection"
        })

    def test_queue_output_valid_creation(self):
        output = QueueOutput(name="res",
                             queue_name="dummy_queue_out",
                             connection="dummy_connection",
                             data_type=DataType.UNDEFINED)

        self.assertEqual(output.get_binding_name(), "queue")
        self.assertEqual(output.get_dict_repr(), {
            "type": "queue",
            "direction": str(BindingDirection.OUT),
            "name": "res",
            "dataType": str(DataType.UNDEFINED),
            "queueName": "dummy_queue_out",
            "connection": "dummy_connection"
        })
