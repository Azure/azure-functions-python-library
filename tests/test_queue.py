# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import unittest

import azure.functions as func
import azure.functions.queue as azf_q


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
        check_input_type = (
            azf_q.QueueMessageInConverter.check_input_type_annotation
        )
        self.assertTrue(check_input_type(func.QueueMessage))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))

    def test_QueueMessage_output_type(self):
        check_output_type = (
            azf_q.QueueMessageOutConverter.check_output_type_annotation
        )
        self.assertTrue(check_output_type(func.QueueMessage))
        self.assertTrue(check_output_type(str))
        self.assertTrue(check_output_type(bytes))
