# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from typing import Dict

from azure.functions.decorators.core import BindingDirection, DataType, \
    InputBinding, OutputBinding, Trigger, AuthLevel


class DummyTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return "Dummy"

    def get_dict_repr(self) -> Dict[str, str]:
        return {
            "type": self.type,
            "direction": self.direction.name,
            "name": self.name,
            "dataType": self.data_type.name
        }

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class DummyInputBinding(InputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyInputBinding"

    def get_dict_repr(self) -> Dict[str, str]:
        return {
            "type": self.type,
            "direction": self.direction.name,
            "name": self.name,
            "dataType": self.data_type.name
        }

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class DummyOutputBinding(OutputBinding):
    @staticmethod
    def get_binding_name() -> str:
        return "DummyOutputBinding"

    def get_dict_repr(self) -> Dict[str, str]:
        return {
            "type": self.type,
            "direction": self.direction.name,
            "name": self.name,
            "dataType": self.data_type.name
        }

    def __init__(self,
                 name: str,
                 data_type: DataType = DataType.UNDEFINED):
        super().__init__(name=name, data_type=data_type)


class TestTriggers(unittest.TestCase):
    def test_binding_direction_all_values(self):
        self.assertEqual([e for e in BindingDirection],
                         [BindingDirection.IN, BindingDirection.OUT,
                          BindingDirection.INOUT])

    def test_data_type_all_values(self):
        self.assertEqual([e for e in DataType],
                         [DataType.UNDEFINED, DataType.STRING, DataType.BINARY,
                          DataType.STREAM])

    def test_auth_level_all_values(self):
        self.assertEqual([e for e in AuthLevel],
                         [AuthLevel.FUNCTION, AuthLevel.ANONYMOUS,
                          AuthLevel.ADMIN])

    def test_trigger_creation(self):
        """Testing if the trigger creation sets the correct values by default
        """
        test_trigger = DummyTrigger(name="dummy", data_type=DataType.UNDEFINED)

        self.assertTrue(test_trigger.is_trigger)
        self.assertEqual(test_trigger.get_dict_repr(),
                         {'dataType': str(DataType.UNDEFINED),
                          'direction': str(BindingDirection.IN),
                          'name': 'dummy',
                          'type': 'Dummy'})

    def test_input_creation(self):
        """Testing if the input creation sets the correct values by default
        """
        test_input = DummyInputBinding(name="dummy",
                                       data_type=DataType.UNDEFINED)

        self.assertFalse(test_input.is_trigger)
        self.assertEqual(test_input.get_dict_repr(),
                         {'dataType': str(DataType.UNDEFINED),
                          'direction': str(BindingDirection.IN),
                          'name': 'dummy',
                          'type': 'DummyInputBinding'})

    def test_output_creation(self):
        """Testing if the output creation sets the correct values by default
        """
        test_output = DummyOutputBinding(name="dummy",
                                         data_type=DataType.UNDEFINED)

        self.assertFalse(test_output.is_trigger)
        self.assertEqual(test_output.get_dict_repr(),
                         {'dataType': str(DataType.UNDEFINED),
                          'direction': str(BindingDirection.OUT),
                          'name': 'dummy',
                          'type': 'DummyOutputBinding'})
