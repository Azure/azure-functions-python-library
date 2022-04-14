# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

from azure.functions.decorators.core import BindingDirection, DataType, \
    InputBinding, OutputBinding, Trigger


class DummyTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return "Dummy"

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class DummyInputBinding(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyInputBinding"

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class DummyOutputBinding(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyOutputBinding"

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class TestBindings(unittest.TestCase):
    def test_trigger_creation(self):
        """Testing if the trigger creation sets the correct values by default
        """
        test_trigger = DummyTrigger(name="dummy", data_type=DataType.UNDEFINED)

        self.assertTrue(test_trigger.is_trigger)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.IN,
                         'name': 'dummy',
                         'type': 'Dummy'}
        self.assertEqual(test_trigger.get_binding_name(), "Dummy")
        self.assertEqual(test_trigger.get_dict_repr(), expected_dict)

    def test_input_creation(self):
        """Testing if the input creation sets the correct values by default
        """
        test_input = DummyInputBinding(name="dummy",
                                       data_type=DataType.UNDEFINED)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.IN,
                         'name': 'dummy',
                         'type': 'DummyInputBinding'}

        self.assertEqual(test_input.get_binding_name(), "DummyInputBinding")
        self.assertFalse(test_input.is_trigger)
        self.assertEqual(test_input.get_dict_repr(), expected_dict)

    def test_output_creation(self):
        """Testing if the output creation sets the correct values by default
        """
        test_output = DummyOutputBinding(name="dummy",
                                         data_type=DataType.UNDEFINED)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.OUT,
                         'name': 'dummy',
                         'type': 'DummyOutputBinding'}

        self.assertEqual(test_output.get_binding_name(), "DummyOutputBinding")
        self.assertFalse(test_output.is_trigger)
        self.assertEqual(test_output.get_dict_repr(), expected_dict)
