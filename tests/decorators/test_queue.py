#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import QUEUE_TRIGGER, QUEUE
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.queue import QueueTrigger, QueueOutput


class TestQueue(unittest.TestCase):
    def test_queue_trigger_valid_creation(self):
        trigger = QueueTrigger(name="req",
                               queue_name="dummy_queue",
                               connection="dummy_connection",
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "queueTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": QUEUE_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "queueName": "dummy_queue",
            "connection": "dummy_connection"
        })

    def test_queue_output_valid_creation(self):
        output = QueueOutput(name="res",
                             queue_name="dummy_queue_out",
                             connection="dummy_connection",
                             data_type=DataType.UNDEFINED,
                             dummy_field="dummy")

        self.assertEqual(output.get_binding_name(), "queue")
        self.assertEqual(output.get_dict_repr(), {
            "type": QUEUE,
            "direction": BindingDirection.OUT,
            'dummyField': 'dummy',
            "name": "res",
            "dataType": DataType.UNDEFINED,
            "queueName": "dummy_queue_out",
            "connection": "dummy_connection"
        })
