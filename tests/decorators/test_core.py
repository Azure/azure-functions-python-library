# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from typing import Dict

from azure.functions.decorators.core import BindingDirection, DataType, \
    InputBinding, \
    OutputBinding, Trigger


class DummyTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return "Dummy"

    def get_dict_repr(self) -> Dict[str, str]:
        return {"dummy": "trigger"}

    def __init__(self):
        super(DummyTrigger, self).__init__(name="Dummy")


class DummyInputBinding(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyInputBinding"

    def get_dict_repr(self) -> Dict[str, str]:
        return {"dummy": "input"}

    def __init__(self):
        super(DummyInputBinding, self).__init__(name="DummyInputBinding")


class DummyOutputBinding(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyOutputBinding"

    def get_dict_repr(self) -> Dict[str, str]:
        return {"dummy": "output"}

    def __init__(self):
        super(DummyOutputBinding, self).__init__(name="DummyOutputBinding")


class TestTriggers(unittest.TestCase):
    def test_trigger_creation(self):
        """Testing if the trigger creation sets the correct values by default
        """
        test_trigger = DummyTrigger()

        self.assertTrue(test_trigger.is_trigger)
        self.assertEqual(test_trigger._name, "Dummy")
        self.assertEqual(test_trigger.type, "Dummy")
        self.assertEqual(test_trigger.get_dict_repr(), {"dummy": "trigger"})
        self.assertEqual(test_trigger.direction, BindingDirection.IN.value)
        self.assertEqual(test_trigger.data_type, DataType.UNDEFINED.value)
