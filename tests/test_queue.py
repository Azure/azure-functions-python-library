# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest
from datetime import date
import azure.functions as func
import azure.functions.queue as azf_q
from azure.functions.meta import Datum, _BaseConverter


class TestQueue(unittest.TestCase):
    def test_QueueMessage_initialize_without_args(self):
        # given
        expected_id = None
        expected_body = b""
        expected_pop_receipt = None

        # when
        test_queue_message = func.QueueMessage()

        # then
        assert expected_id == test_queue_message.id
        assert expected_body == test_queue_message.get_body()
        assert expected_pop_receipt == test_queue_message.pop_receipt

    def test_QueueMessage_initialize_all_arguments(self):
        # given
        expected_id: str = "Identifier"
        expected_body: bytes = b"Body"
        expected_pop_receipt: str = "Pop Receipt"

        # when
        test_queue_message = func.QueueMessage(
            id=expected_id,
            body=expected_body,
            pop_receipt=expected_pop_receipt
        )

        # then
        assert expected_id == test_queue_message.id
        assert expected_body == test_queue_message.get_body()
        assert expected_pop_receipt == test_queue_message.pop_receipt

    def test_QueueMessage_get_json(self):
        # given
        test_body: str = '{"isJSON": "True"}'
        expected_body = json.loads(test_body)

        # when
        test_queue_message = func.QueueMessage(
            body=test_body
        )

        # then
        assert expected_body == test_queue_message.get_json()

    def test_QueueMessage_input_type(self):
        # when
        check_input_type = (
            azf_q.QueueMessageInConverter.check_input_type_annotation
        )

        # then
        self.assertTrue(check_input_type(func.QueueMessage))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))

    def test_QueueMessage_output_type(self):
        # when
        check_output_type = (
            azf_q.QueueMessageOutConverter.check_output_type_annotation
        )

        # then
        self.assertTrue(check_output_type(func.QueueMessage))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(bytes))

    def test_queue_message_initialize_all_args(self):
        # given
        expiration_time = date(2022, 5, 1)
        insertion_time = date(2022, 6, 2)
        time_next_visible = date(2022, 7, 3)

        # when
        queue_message = azf_q.QueueMessage(id="1",
                                           body="test_body",
                                           dequeue_count=10,
                                           expiration_time=expiration_time,
                                           insertion_time=insertion_time,
                                           time_next_visible=time_next_visible,
                                           pop_receipt="dummy_pop_receipt")

        # then
        self.assertEqual(queue_message.dequeue_count, 10)
        self.assertEqual(queue_message.expiration_time, expiration_time)
        self.assertEqual(queue_message.insertion_time, insertion_time)
        self.assertEqual(queue_message.time_next_visible, time_next_visible)
        self.assertEqual(queue_message.pop_receipt, "dummy_pop_receipt")
        self.assertEqual(queue_message.get_body(), b"test_body")
        self.assertEqual(queue_message.id, "1")

    def test_queue_message_in_converter_decode(self):
        # given
        data = Datum("test_body", "string")
        trigger_metadata = {
            "Id": Datum("1", "string"),
            "DequeueCount": Datum(10, "int"),
            "ExpirationTime": Datum("2021-12-12T03:16:34Z", "string"),
            "InsertionTime": Datum("2022-1-12T03:16:34Z", "string"),
            "NextVisibleTime": Datum("2022-2-12T03:16:34Z", "string"),
            "PopReceipt": Datum("dummy_pop_receipt", "string")
        }

        # when
        queue_message = azf_q.QueueMessageInConverter.decode(
            data=data,
            trigger_metadata=trigger_metadata)

        # then
        self.assertEqual(queue_message.dequeue_count, 10)
        self.assertEqual(
            queue_message.expiration_time,
            _BaseConverter._parse_datetime('2021-12-12T03:16:34Z'))
        self.assertEqual(queue_message.insertion_time,
                         _BaseConverter._parse_datetime('2022-1-12T03:16:34Z'))
        self.assertEqual(queue_message.time_next_visible,
                         _BaseConverter._parse_datetime('2022-2-12T03:16:34Z'))
        self.assertEqual(queue_message.pop_receipt, "dummy_pop_receipt")
        self.assertEqual(queue_message.get_body(), b"test_body")
        self.assertEqual(queue_message.id, "1")

    def test_queue_message_invalid_data_type(self):
        # given
        data = Datum(10, "int")
        is_exception_raised = False

        # when
        try:
            azf_q.QueueMessageInConverter.decode(data=data,
                                                 trigger_metadata={})
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_queue_message_trigger_metadata_exception(self):
        # given
        data = Datum("test_body", "string")
        is_exception_raised = False

        # when
        try:
            azf_q.QueueMessageInConverter.decode(
                data=data, trigger_metadata=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_queue_message_encode_str_data(self):
        # when
        data = azf_q.QueueMessageOutConverter.encode(obj="test_string",
                                                     expected_type=None)

        # then
        self.assertEqual(data.type, "string")
        self.assertEqual(data.value, "test_string")

    def test_queue_message_encode_bytes_data(self):

        data = azf_q.QueueMessageOutConverter.encode(obj=b"test_string",
                                                     expected_type=None)

        self.assertEqual(data.type, "bytes")
        self.assertEqual(data.value, b"test_string")

    def test_queue_message_encode_json_data(self):
        # given
        q_message = azf_q.QueueMessage(id="1", body="test_body")
        expected_value = json.dumps({
            'id': "1",
            'body': 'test_body'
        })

        # when
        data = azf_q.QueueMessageOutConverter.encode(obj=q_message,
                                                     expected_type=None)

        # then
        self.assertEqual(data.type, "json")
        self.assertEqual(data.value, expected_value)

    def test_queue_message_encode_obj_iterable(self):
        # given
        q_messages = ["test_string",
                      azf_q.QueueMessage(id="1", body="test_body")]
        expected_value = json.dumps(["test_string", {
            'id': "1",
            'body': 'test_body'
        }])

        # when
        data = azf_q.QueueMessageOutConverter.encode(obj=q_messages,
                                                     expected_type=None)

        # then
        self.assertEqual(data.type, "json")
        self.assertEqual(data.value, expected_value)

    def test_queue_message_encode_invalid_data_type_exception(self):
        # given
        q_messages = ["test_string",
                      azf_q.QueueMessage(id="1", body="test_body"),
                      5]
        is_exception_raised = False
        # when
        try:
            azf_q.QueueMessageOutConverter.encode(obj=q_messages,
                                                  expected_type=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)

    def test_queue_message_encode_no_implementation_exception(self):
        is_exception_raised = False
        # when
        try:
            azf_q.QueueMessageOutConverter.encode(obj=1,
                                                  expected_type=None)
        except NotImplementedError:
            is_exception_raised = True

        # then
        self.assertTrue(is_exception_raised)
