#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import WARMUP_TRIGGER
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.warmup import WarmUpTrigger


class TestWarmUp(unittest.TestCase):
    def test_warmup_trigger_valid_creation(self):
        trigger = WarmUpTrigger(name="req",
                                data_type=DataType.UNDEFINED,
                                dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "warmupTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": WARMUP_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED
        })
