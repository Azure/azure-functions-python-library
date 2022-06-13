#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest
from azure.functions.decorators.constants import TABLE
from azure.functions.decorators.table import TableInput, TableOutput
from azure.functions.decorators.core import BindingDirection, DataType


class TestTable(unittest.TestCase):
    def test_table_input_valid_creation(self):
        table_input = TableInput(name="in",
                                 table_name="dummy_table_name",
                                 connection="dummy_in_conn",
                                 row_key="dummy_key",
                                 partition_key="dummy_partition_key",
                                 take=1,
                                 filter="dummy_filter",
                                 data_type=DataType.UNDEFINED)

        self.assertEqual(table_input.get_binding_name(), TABLE)
        self.assertEqual(table_input.get_dict_repr(), {
            "direction": BindingDirection.IN,
            "dataType": DataType.UNDEFINED,
            "type": "table",
            "name": "in",
            "tableName": "dummy_table_name",
            "connection": "dummy_in_conn",
            "rowKey": "dummy_key",
            "partitionKey": "dummy_partition_key",
            "take": 1,
            "filter": "dummy_filter"
        })

    def test_table_output_valid_creation(self):
        table_output = TableOutput(name="out",
                                   table_name="dummy_table_name",
                                   row_key="dummy_key",
                                   partition_key="dummy_partition_key",
                                   connection="dummy_out_conn",
                                   data_type=DataType.UNDEFINED)

        self.assertEqual(table_output.get_binding_name(), TABLE)
        self.assertEqual(table_output.get_dict_repr(), {
            "direction": BindingDirection.OUT,
            "dataType": DataType.UNDEFINED,
            "type": "table",
            "name": "out",
            "tableName": "dummy_table_name",
            "connection": "dummy_out_conn",
            "rowKey": "dummy_key",
            "partitionKey": "dummy_partition_key"
        })
