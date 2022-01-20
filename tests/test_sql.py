# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

import azure.functions as func
import azure.functions.sql as sql
from azure.functions.meta import Datum


class TestSql(unittest.TestCase):
    def test_sql_convert_none(self):
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=None, trigger_metadata=None)
        self.assertIsNone(result)

    def test_sql_convert_string(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "string")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test')

    def test_sql_convert_bytes(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """.encode(), "bytes")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test')

    def test_sql_convert_json(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "test"
        }
        """, "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test')

    def test_sql_convert_json_name_is_null(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": null
        }
        """, "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], None)

    def test_sql_convert_json_multiple_entries(self):
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
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'test1')
        self.assertEqual(result[1]['name'], 'test2')

    def test_sql_convert_json_multiple_nulls(self):
        datum: Datum = Datum("[null]", "json")
        result: func.SqlRowList = sql.SqlConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], None)

    def test_sql_input_type(self):
        check_input_type = sql.SqlConverter.check_input_type_annotation
        self.assertTrue(check_input_type(func.SqlRowList))
        self.assertFalse(check_input_type(func.SqlRow))
        self.assertFalse(check_input_type(str))

    def test_sql_output_type(self):
        check_output_type = sql.SqlConverter.check_output_type_annotation
        self.assertTrue(check_output_type(func.SqlRowList))
        self.assertTrue(check_output_type(func.SqlRow))
        self.assertFalse(check_output_type(str))
