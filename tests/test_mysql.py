# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

import azure.functions as func
import azure.functions.mysql as mysql
from azure.functions.meta import Datum


class TestMySql(unittest.TestCase):
    def test_mysql_decode_none(self):
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=None, trigger_metadata=None)
        self.assertIsNone(result)

    def test_mysql_decode_string(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "string")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'MySqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'MySqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'MySqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'MySqlRow item should have name test')

    def test_mysql_decode_bytes(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """.encode(), "bytes")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'MySqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'MySqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'MySqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'MySqlRow item should have name test')

    def test_mysql_decode_json(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'MySqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'MySqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'MySqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'MySqlRow item should have name test')

    def test_mysql_decode_json_name_is_null(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": null
        }
        """, "json")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'MySqlRowList itself should be non-None')
        self.assertEqual(len(result),
                         1,
                         'MySqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['name'],
                         None,
                         'Item in MySqlRowList should be None')

    def test_mysql_decode_json_multiple_entries(self):
        datum: Datum = Datum("""
        [
            {
                "id": "1",
                "name": "test1"
            },
            {
                "id": "2",
                "name": "test2"
            }
        ]
        """, "json")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result),
                         2,
                         'MySqlRowList should have exactly 2 items')
        self.assertEqual(result[0]['id'],
                         '1',
                         'First MySqlRowList item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test1',
                         'First MySqlRowList item should have name test1')
        self.assertEqual(result[1]['id'],
                         '2',
                         'First MySqlRowList item should have id 2')
        self.assertEqual(result[1]['name'],
                         'test2',
                         'Second MySqlRowList item should have name test2')

    def test_mysql_decode_json_multiple_nulls(self):
        datum: Datum = Datum("[null]", "json")
        result: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result),
                         1,
                         'MySqlRowList should have exactly 1 item')
        self.assertEqual(result[0],
                         None,
                         'MySqlRow item should be None')

    def test_mysql_encode_mysqlrow(self):
        mysqlRow = func.MySqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """)
        datum = mysql.MySqlConverter.encode(obj=mysqlRow, expected_type=None)
        self.assertEqual(datum.type,
                         'json',
                         'Datum type should be JSON')
        self.assertEqual(len(datum.python_value),
                         1,
                         'Encoded value should be list of length 1')
        self.assertEqual(datum.python_value[0]['id'],
                         '1',
                         'id should be 1')
        self.assertEqual(datum.python_value[0]['name'],
                         'test',
                         'name should be test')

    def test_mysql_encode_mysqlrowlist(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        mysqlRowList: func.MySqlRowList = mysql.MySqlConverter.decode(
            data=datum, trigger_metadata=None)
        datum = mysql.MySqlConverter.encode(
            obj=mysqlRowList, expected_type=None)
        self.assertEqual(datum.type,
                         'json',
                         'Datum type should be JSON')
        self.assertEqual(len(datum.python_value),
                         1,
                         'Encoded value should be list of length 1')
        self.assertEqual(datum.python_value[0]['id'],
                         '1',
                         'id should be 1')
        self.assertEqual(datum.python_value[0]['name'],
                         'test',
                         'name should be test')

    def test_mysql_encode_list_of_mysqlrows(self):
        mysqlRows = [
            func.MySqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """),
            func.MySqlRow.from_json("""
            {
                "id": "2",
                "name": "test2"
            }
            """)
        ]
        datum = mysql.MySqlConverter.encode(obj=mysqlRows, expected_type=None)
        self.assertEqual(datum.type,
                         'json',
                         'Datum type should be JSON')
        self.assertEqual(len(datum.python_value),
                         2,
                         'Encoded value should be list of length 2')
        self.assertEqual(datum.python_value[0]['id'],
                         '1',
                         'id should be 1')
        self.assertEqual(datum.python_value[0]['name'],
                         'test',
                         'name should be test')
        self.assertEqual(datum.python_value[1]['id'],
                         '2',
                         'id should be 2')
        self.assertEqual(datum.python_value[1]['name'],
                         'test2',
                         'name should be test2')

    def test_mysql_encode_list_of_str_raises(self):
        strList = [
            """
        {
            "id": "1",
            "name": "test"
        }
        """
        ]
        self.assertRaises(NotImplementedError,
                          mysql.MySqlConverter.encode,
                          obj=strList,
                          expected_type=None)

    def test_mysql_encode_list_of_mysqlrowlist_raises(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        mysqlRowListList = [
            mysql.MySqlConverter.decode(
                data=datum, trigger_metadata=None)
        ]
        self.assertRaises(NotImplementedError,
                          mysql.MySqlConverter.encode,
                          obj=mysqlRowListList,
                          expected_type=None)

    def test_mysql_input_type(self):
        check_input_type = mysql.MySqlConverter.check_input_type_annotation
        self.assertTrue(check_input_type(func.MySqlRowList),
                        'MySqlRowList should be accepted')
        self.assertFalse(check_input_type(func.MySqlRow),
                         'MySqlRow should not be accepted')
        self.assertFalse(check_input_type(str),
                         'str should not be accepted')

    def test_mysql_output_type(self):
        check_output_type = mysql.MySqlConverter.check_output_type_annotation
        self.assertTrue(check_output_type(func.MySqlRowList),
                        'MySqlRowList should be accepted')
        self.assertTrue(check_output_type(func.MySqlRow),
                        'MySqlRow should be accepted')
        self.assertFalse(check_output_type(str),
                         'str should not be accepted')

    def test_mysqlrow_json(self):
        # Parse MySqlRow from JSON
        mysqlRow = func.MySqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """)
        self.assertEqual(mysqlRow['id'],
                         '1',
                         'Parsed MySqlRow id should be 1')
        self.assertEqual(mysqlRow['name'],
                         'test',
                         'Parsed MySqlRow name should be test')

        # Parse JSON from MySqlRow
        mysqlRowJson = json.loads(func.MySqlRow.to_json(mysqlRow))
        self.assertEqual(mysqlRowJson['id'],
                         '1',
                         'Parsed JSON id should be 1')
        self.assertEqual(mysqlRowJson['name'],
                         'test',
                         'Parsed JSON name should be test')
