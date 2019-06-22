import azure.functions as func
import json

def test_QueueMessage_initialize_without_args():
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


def test_QueueMessage_initialize_all_arguments():
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


def test_QueueMessage_get_json():
    # given
    test_body: str = '{"isJSON": "True"}'
    expected_body = json.loads(test_body)

    # when
    test_queue_message = func.QueueMessage(
        body=test_body
    )

    # then
    assert expected_body == test_queue_message.get_json()
