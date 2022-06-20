# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

import azure.functions as func
import azure.functions.cosmosdb as cdb
from azure.functions.meta import Datum


class TestCosmosdb(unittest.TestCase):
    def test_cosmosdb_convert_none(self):
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=None, trigger_metadata=None)
        self.assertIsNone(result)

    def test_cosmosdb_convert_string(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "awesome_name"
        }
        """, "string")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'awesome_name')

    def test_cosmosdb_convert_bytes(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "awesome_name"
        }
        """.encode(), "bytes")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'awesome_name')

    def test_cosmosdb_convert_json(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": "awesome_name"
        }
        """, "json")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'awesome_name')

    def test_cosmosdb_convert_json_name_is_null(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": null
        }
        """, "json")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], None)

    def test_cosmosdb_convert_json_internal_fields_assigned(self):
        datum: Datum = Datum("""
        {
            "id": "1",
            "name": null,
            "_rid": "dummy12344",
            "_self": "7U4=/docs/gpU4AJcm7U4KAAAAAAAAAA==/",
            "_etag": "000-0500-0000-62598ff00000",
            "_attachments": "attachments/",
            "_ts": 1650036720
        }
        """, "json")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], None)
        self.assertEqual(result[0]['_rid'], "dummy12344")
        self.assertEqual(result[0]['_self'],
                         "7U4=/docs/gpU4AJcm7U4KAAAAAAAAAA==/")
        self.assertEqual(result[0]['_etag'], "000-0500-0000-62598ff00000")
        self.assertEqual(result[0]['_attachments'], "attachments/")
        self.assertEqual(result[0]['_ts'], 1650036720)

    def test_cosmosdb_convert_json_multiple_entries(self):
        datum: Datum = Datum("""
        [
            {
                "id": "1",
                "name": "awesome_name"
            },
            {
                "id": "2",
                "name": "bossy_name"
            }
        ]
        """, "json")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'awesome_name')
        self.assertEqual(result[1]['name'], 'bossy_name')

    def test_cosmosdb_convert_json_multiple_nulls(self):
        datum: Datum = Datum("[null]", "json")
        result: func.DocumentList = cdb.CosmosDBConverter.decode(
            data=datum, trigger_metadata=None)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], None)

    def test_cosmosdb_input_type(self):
        check_input_type = cdb.CosmosDBConverter.check_input_type_annotation
        self.assertTrue(check_input_type(func.DocumentList))
        self.assertFalse(check_input_type(func.Document))
        self.assertFalse(check_input_type(str))

    def test_cosmosdb_output_type(self):
        check_output_type = cdb.CosmosDBConverter.check_output_type_annotation
        self.assertTrue(check_output_type(func.DocumentList))
        self.assertTrue(check_output_type(func.Document))
        self.assertFalse(check_output_type(str))

    def test_cosmosdb_encode_document(self):
        doc = cdb.cdb.Document({"dummy_key": "dummy_val"})

        # when
        result = cdb.CosmosDBConverter.encode(obj=doc, expected_type=None)

        # then
        expected_value = '[{"dummy_key": "dummy_val"}]'
        self.assertEqual(result.type, "json")
        self.assertEqual(result.value, expected_value)

    def test_cosmosdb_encode_document_list(self):
        doc1 = cdb.cdb.Document({"dummy_key1": "dummy_val2"})
        doc2 = cdb.cdb.Document({"dummy_key2": "dummy_val2"})

        doc_list = cdb.cdb.DocumentList([doc1, doc2])

        # when
        result = cdb.CosmosDBConverter.encode(obj=doc_list, expected_type=None)

        # then
        expected_value = \
            '[{"dummy_key1": "dummy_val2"}, {"dummy_key2": "dummy_val2"}]'
        self.assertEqual(result.type, "json")
        self.assertEqual(result.value, expected_value)

    def test_cosmosdb_encode_obj_iterable(self):
        doc1 = cdb.cdb.Document({"dummy_key1": "dummy_val2"})
        doc2 = cdb.cdb.Document({"dummy_key2": "dummy_val2"})

        doc_list_iterable = [doc1, doc2]

        # when
        result = cdb.CosmosDBConverter.encode(
            obj=doc_list_iterable, expected_type=None)

        # then
        expected_value = \
            '[{"dummy_key1": "dummy_val2"}, {"dummy_key2": "dummy_val2"}]'
        self.assertEqual(result.type, "json")
        self.assertEqual(result.value, expected_value)

    def test_cosmosdb_encode_no_implementation_exception(self):
        is_exception_raised = False
        # when
        try:
            cdb.CosmosDBConverter.encode(obj=1,
                                         expected_type=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_cosmosdb_encode_no_implementation_exception1(self):
        is_exception_raised = False

        # when
        try:
            cdb.CosmosDBConverter.encode(obj=[1],
                                         expected_type=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)
