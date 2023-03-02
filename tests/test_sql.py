# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

import azure.functions as func
import azure.functions.sql as sql
from azure.functions.meta import Datum


class TestSql(unittest.TestCase):
    def test_sql_decode_none(self):
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=None, trigger_metadata=None)
        self.assertIsNone(result)

    def test_sql_decode_string(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "string")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'SqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'SqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'SqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'SqlRow item should have name test')

    def test_sql_decode_bytes(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """.encode(), "bytes")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'SqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'SqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'SqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'SqlRow item should have name test')

    def test_sql_decode_json(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'SqlRowList should be non-None')
        self.assertEqual(len(result),
                         1,
                         'SqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['id'],
                         '1',
                         'SqlRow item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test',
                         'SqlRow item should have name test')

    def test_sql_decode_json_name_is_null(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": null
        }
        """, "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result,
                             'SqlRowList itself should be non-None')
        self.assertEqual(len(result),
                         1,
                         'SqlRowList should have exactly 1 item')
        self.assertEqual(result[0]['name'],
                         None,
                         'Item in SqlRowList should be None')

    def test_sql_decode_json_multiple_entries(self):
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
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result),
                         2,
                         'SqlRowList should have exactly 2 items')
        self.assertEqual(result[0]['id'],
                         '1',
                         'First SqlRowList item should have id 1')
        self.assertEqual(result[0]['name'],
                         'test1',
                         'First SqlRowList item should have name test1')
        self.assertEqual(result[1]['id'],
                         '2',
                         'First SqlRowList item should have id 2')
        self.assertEqual(result[1]['name'],
                         'test2',
                         'Second SqlRowList item should have name test2')

    def test_sql_decode_json_multiple_nulls(self):
        datum: Datum = Datum("[null]", "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result),
                         1,
                         'SqlRowList should have exactly 1 item')
        self.assertEqual(result[0],
                         None,
                         'SqlRow item should be None')

    def test_sql_encode_sqlrow(self):
        sqlRow = func.SqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """)
        datum = sql.SqlConverter.encode(obj=sqlRow, expected_type=None)
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

    def test_sql_encode_sqlrowlist(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        sqlRowList: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        datum = sql.SqlConverter.encode(obj=sqlRowList, expected_type=None)
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

    def test_sql_encode_list_of_sqlrows(self):
        sqlRows = [
            func.SqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """),
            func.SqlRow.from_json("""
            {
                "id": "2",
                "name": "test2"
            }
            """)
        ]
        datum = sql.SqlConverter.encode(obj=sqlRows, expected_type=None)
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

    def test_sql_encode_list_of_str_raises(self):
        strList = [
            """
        {
            "id": "1",
            "name": "test"
        }
        """
        ]
        self.assertRaises(NotImplementedError,
                          sql.SqlConverter.encode,
                          obj=strList,
                          expected_type=None)

    def test_sql_encode_list_of_sqlrowlist_raises(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        sqlRowListList = [
            sql.SqlConverter.decode(
                data=datum, trigger_metadata=None)
        ]
        self.assertRaises(NotImplementedError,
                          sql.SqlConverter.encode,
                          obj=sqlRowListList,
                          expected_type=None)

    def test_sql_input_type(self):
        check_input_type = sql.SqlConverter.check_input_type_annotation
        self.assertTrue(check_input_type(func.SqlRowList),
                        'SqlRowList should be accepted')
        self.assertFalse(check_input_type(func.SqlRow),
                         'SqlRow should not be accepted')
        self.assertFalse(check_input_type(str),
                         'str should not be accepted')

    def test_sql_output_type(self):
        check_output_type = sql.SqlConverter.check_output_type_annotation
        self.assertTrue(check_output_type(func.SqlRowList),
                        'SqlRowList should be accepted')
        self.assertTrue(check_output_type(func.SqlRow),
                        'SqlRow should be accepted')
        self.assertFalse(check_output_type(str),
                         'str should not be accepted')

    def test_sqlrow_json(self):
        # Parse SqlRow from JSON
        sqlRow = func.SqlRow.from_json("""
        {
            "id": "1",
            "name": "test"
        }
        """)
        self.assertEqual(sqlRow['id'],
                         '1',
                         'Parsed SqlRow id should be 1')
        self.assertEqual(sqlRow['name'],
                         'test',
                         'Parsed SqlRow name should be test')

        # Parse JSON from SqlRow
        sqlRowJson = json.loads(func.SqlRow.to_json(sqlRow))
        self.assertEqual(sqlRowJson['id'],
                         '1',
                         'Parsed JSON id should be 1')
        self.assertEqual(sqlRowJson['name'],
                         'test',
                         'Parsed JSON name should be test')
