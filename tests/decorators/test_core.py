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
                 data_type: DataType = DataType.UNDEFINED,
                 **kwargs):
        super().__init__(name=name, data_type=data_type)


class DummyInputBinding(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyInputBinding"

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED,
                 **kwargs):
        super().__init__(name=name, data_type=data_type)


class DummyOutputBinding(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyOutputBinding"

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED,
                 **kwargs):
        super().__init__(name=name, data_type=data_type)


class TestBindings(unittest.TestCase):
    def test_trigger_creation(self):
        test_trigger = DummyTrigger(name="dummy", data_type=DataType.UNDEFINED)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.IN,
                         'name': 'dummy',
                         'type': 'Dummy'}
        self.assertEqual(test_trigger.get_binding_name(), "Dummy")
        self.assertEqual(test_trigger.get_dict_repr(), expected_dict)

    def test_param_direction_unset(self):
        test_trigger = DummyTrigger(name="dummy", data_type=DataType.UNDEFINED,
                                    direction="dummy", type="hello")

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.IN,
                         'name': 'dummy',
                         'type': 'Dummy'}
        self.assertEqual(test_trigger.get_binding_name(), "Dummy")
        self.assertEqual(test_trigger.get_dict_repr(), expected_dict)

    def test_input_creation(self):
        test_input = DummyInputBinding(name="dummy",
                                       data_type=DataType.UNDEFINED)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.IN,
                         'name': 'dummy',
                         'type': 'DummyInputBinding'}

        self.assertEqual(test_input.get_binding_name(), "DummyInputBinding")
        self.assertEqual(test_input.get_dict_repr(), expected_dict)

    def test_output_creation(self):
        test_output = DummyOutputBinding(name="dummy",
                                         data_type=DataType.UNDEFINED)

        expected_dict = {'dataType': DataType.UNDEFINED,
                         'direction': BindingDirection.OUT,
                         'name': 'dummy',
                         'type': 'DummyOutputBinding'}

        self.assertEqual(test_output.get_binding_name(), "DummyOutputBinding")
        self.assertEqual(test_output.get_dict_repr(), expected_dict)

    def test_supported_trigger_types_populated(self):
        for supported_trigger in Trigger.__subclasses__():
            trigger_name = supported_trigger.__name__
            if trigger_name != "GenericTrigger":
                trigger_type_name = supported_trigger.get_binding_name()
                self.assertTrue(trigger_type_name is not None,
                                f"binding_type {trigger_name} can not be "
                                f"None!")
                self.assertTrue(len(trigger_type_name) > 0,
                                f"binding_type {trigger_name} can not be "
                                f"empty str!")
