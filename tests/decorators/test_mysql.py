#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import MYSQL, MYSQL_TRIGGER
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.mysql import MySqlInput, \
    MySqlOutput, MySqlTrigger


class TestMySql(unittest.TestCase):
    def test_mysql_input_valid_creation(self):
        input = MySqlInput(name="req",
                           command_text="dummy_query",
                           connection_string_setting="dummy_setting",
                           data_type=DataType.UNDEFINED,
                           dummy_field="dummy")
        self.assertEqual(input.get_binding_name(), "mysql")
        self.assertEqual(input.get_dict_repr(),
                         {"commandText": "dummy_query",
                          "connectionStringSetting": "dummy_setting",
                          "commandType": "Text",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy",
                          "name": "req",
                          "type": MYSQL})

    def test_mysql_output_valid_creation(self):
        output = MySqlOutput(name="req",
                             command_text="dummy_table",
                             connection_string_setting="dummy_setting",
                             data_type=DataType.UNDEFINED,
                             dummy_field="dummy")
        self.assertEqual(output.get_binding_name(), "mysql")
        self.assertEqual(output.get_dict_repr(),
                         {"commandText": "dummy_table",
                          "connectionStringSetting": "dummy_setting",
                          "dataType": DataType.UNDEFINED,
                          "direction": BindingDirection.OUT,
                          "dummyField": "dummy",
                          "name": "req",
                          "type": MYSQL})

    def test_mysql_trigger_valid_creation(self):
        trigger = MySqlTrigger(name="req",
                               table_name="dummy_table",
                               connection_string_setting="dummy_setting",
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "mysqlTrigger")
        self.assertEqual(trigger.get_dict_repr(),
                         {"connectionStringSetting": "dummy_setting",
                          "dataType": DataType.UNDEFINED,
                          "tableName": "dummy_table",
                          "direction": BindingDirection.IN,
                          "dummyField": "dummy",
                          "name": "req",
                          "type": MYSQL_TRIGGER})
