# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Tests for the uniform to_dict() / to_json() serialization contract."""

import base64
import datetime
import json
import unittest

import azure.functions as func
from azure.functions._utils import _serialize_value


class TestSerializeValue(unittest.TestCase):
    def test_bytes_utf8(self):
        assert _serialize_value(b"hello") == "hello"

    def test_bytes_non_utf8(self):
        raw = bytes([0xFF, 0xFE])
        result = _serialize_value(raw)
        assert result == {
            "__encoding": "base64",
            "value": base64.b64encode(raw).decode("ascii"),
        }

    def test_datetime(self):
        dt = datetime.datetime(2024, 1, 15, 12, 30, 0)
        assert _serialize_value(dt) == "2024-01-15T12:30:00"

    def test_timedelta(self):
        td = datetime.timedelta(hours=1, minutes=30)
        result = _serialize_value(td)
        assert isinstance(result, str)
        assert "1:30:00" in result

    def test_passthrough_str(self):
        assert _serialize_value("hello") == "hello"

    def test_passthrough_int(self):
        assert _serialize_value(42) == 42

    def test_passthrough_none(self):
        assert _serialize_value(None) is None


class TestQueueMessageToDict(unittest.TestCase):
    def test_to_dict_defaults(self):
        msg = func.QueueMessage()
        d = msg.to_dict()
        assert d["id"] is None
        assert d["body"] == ""  # b"" decodes to ""
        assert d["pop_receipt"] is None
        assert d["dequeue_count"] is None

    def test_to_dict_with_body(self):
        msg = func.QueueMessage(id="abc", body=b"hello")
        d = msg.to_dict()
        assert d["id"] == "abc"
        assert d["body"] == "hello"

    def test_to_dict_bytes_body_non_utf8(self):
        raw = bytes([0xFF, 0xFE])
        msg = func.QueueMessage(body=raw)
        d = msg.to_dict()
        assert d["body"]["__encoding"] == "base64"

    def test_to_json_returns_string(self):
        msg = func.QueueMessage(id="x", body=b"data")
        s = msg.to_json()
        assert isinstance(s, str)
        parsed = json.loads(s)
        assert parsed["id"] == "x"
        assert parsed["body"] == "data"


class TestEventHubEventToDict(unittest.TestCase):
    def test_to_dict_basic(self):
        from azure.functions._eventhub import EventHubEvent
        evt = EventHubEvent(
            body=b"payload",
            partition_key="pk1",
            sequence_number=42,
            offset="100",
            enqueued_time=datetime.datetime(2024, 6, 1, 10, 0, 0),
        )
        d = evt.to_dict()
        assert d["body"] == "payload"
        assert d["partition_key"] == "pk1"
        assert d["sequence_number"] == 42
        assert d["offset"] == "100"
        assert d["enqueued_time"] == "2024-06-01T10:00:00"
        assert d["iothub_metadata"] is None

    def test_to_json_roundtrip(self):
        from azure.functions._eventhub import EventHubEvent
        evt = EventHubEvent(body=b"test", partition_key="pk")
        parsed = json.loads(evt.to_json())
        assert parsed["body"] == "test"
        assert parsed["partition_key"] == "pk"


class TestEventGridEventToDict(unittest.TestCase):
    def test_to_dict(self):
        evt = func.EventGridEvent(
            id="evt1",
            data={"key": "val"},
            topic="/subscriptions/sub/providers/Microsoft.Storage",
            subject="/blobServices/default/containers/test",
            event_type="Microsoft.Storage.BlobCreated",
            event_time=datetime.datetime(2024, 1, 1, 0, 0, 0),
            data_version="1.0",
        )
        d = evt.to_dict()
        assert d["id"] == "evt1"
        assert d["topic"].startswith("/subscriptions")
        assert d["event_time"] == "2024-01-01T00:00:00"
        assert d["data"] == {"key": "val"}

    def test_to_json(self):
        evt = func.EventGridEvent(
            id="e2",
            data={},
            topic="t",
            subject="s",
            event_type="et",
            event_time=None,
            data_version="1",
        )
        parsed = json.loads(evt.to_json())
        assert parsed["id"] == "e2"
        assert parsed["event_time"] is None


class TestServiceBusMessageToDict(unittest.TestCase):
    def test_stub_to_dict(self):
        # The stub base class (_servicebus.ServiceBusMessage) also has to_dict
        msg = func.ServiceBusMessage(body=b"hello")
        d = msg.to_dict()
        assert d["body"] == "hello"
        assert d["message_id"] == ""  # stub default

    def test_to_json(self):
        msg = func.ServiceBusMessage(body=b"msg")
        parsed = json.loads(msg.to_json())
        assert parsed["body"] == "msg"


class TestTimerRequestToDict(unittest.TestCase):
    def test_base_timer_to_dict(self):
        # The base _timer.TimerRequest
        timer = func.TimerRequest(past_due=True)
        d = timer.to_dict()
        assert d["past_due"] is True

    def test_to_json(self):
        timer = func.TimerRequest()
        parsed = json.loads(timer.to_json())
        assert parsed["past_due"] is False


class TestInputStreamToDict(unittest.TestCase):
    def test_base_blob_to_dict(self):
        blob = func.InputStream(name="myblob", uri="https://x/blob", length=42)
        d = blob.to_dict()
        assert d["name"] == "myblob"
        assert d["uri"] == "https://x/blob"
        assert d["length"] == 42

    def test_to_json(self):
        blob = func.InputStream(name="b", uri="u", length=10)
        parsed = json.loads(blob.to_json())
        assert parsed["name"] == "b"


class TestDocumentToDict(unittest.TestCase):
    def test_document_to_dict(self):
        doc = func.Document.from_dict({"id": "1", "value": 42})
        d = doc.to_dict()
        assert d == {"id": "1", "value": 42}

    def test_document_list_to_dict(self):
        dl = func.DocumentList()
        dl.append(func.Document.from_dict({"a": 1}))
        dl.append(func.Document.from_dict({"b": 2}))
        result = dl.to_dict()
        assert result == [{"a": 1}, {"b": 2}]

    def test_document_list_to_json(self):
        dl = func.DocumentList()
        dl.append(func.Document.from_dict({"x": 10}))
        parsed = json.loads(dl.to_json())
        assert parsed == [{"x": 10}]


class TestSqlRowToDict(unittest.TestCase):
    def test_sql_row_to_dict(self):
        row = func.SqlRow.from_dict({"col1": "a", "col2": 1})
        assert row.to_dict() == {"col1": "a", "col2": 1}

    def test_sql_row_list_to_dict(self):
        rl = func.SqlRowList()
        rl.append(func.SqlRow.from_dict({"k": "v"}))
        assert rl.to_dict() == [{"k": "v"}]

    def test_sql_row_list_to_json(self):
        rl = func.SqlRowList()
        rl.append(func.SqlRow.from_dict({"n": 7}))
        parsed = json.loads(rl.to_json())
        assert parsed == [{"n": 7}]


class TestMySqlRowToDict(unittest.TestCase):
    def test_mysql_row_to_dict(self):
        row = func.MySqlRow.from_dict({"col": "val"})
        assert row.to_dict() == {"col": "val"}

    def test_mysql_row_list_to_dict(self):
        rl = func.MySqlRowList()
        rl.append(func.MySqlRow.from_dict({"x": 5}))
        assert rl.to_dict() == [{"x": 5}]

    def test_mysql_row_list_to_json(self):
        rl = func.MySqlRowList()
        rl.append(func.MySqlRow.from_dict({"y": 9}))
        parsed = json.loads(rl.to_json())
        assert parsed == [{"y": 9}]


class TestKafkaEventToDict(unittest.TestCase):
    def test_to_dict(self):
        from azure.functions.kafka import KafkaEvent
        evt = KafkaEvent(
            body=b"message",
            key="key1",
            offset=5,
            partition=0,
            topic="my-topic",
            timestamp="2024-01-01T00:00:00",
        )
        d = evt.to_dict()
        assert d["body"] == "message"
        assert d["key"] == "key1"
        assert d["topic"] == "my-topic"

    def test_to_json(self):
        from azure.functions.kafka import KafkaEvent
        evt = KafkaEvent(body=b"k", topic="t", key="k1", offset=0, partition=1,
                         timestamp="ts")
        parsed = json.loads(evt.to_json())
        assert parsed["body"] == "k"


class TestCloudEventToDict(unittest.TestCase):
    def test_to_dict(self):
        evt = func.CloudEvent(
            id="ce1",
            source="https://example.com/source",
            type="com.example.someevent",
            specversion="1.0",
            data={"key": "value"},
            time=datetime.datetime(2024, 3, 1, 12, 0, 0),
        )
        d = evt.to_dict()
        assert d["id"] == "ce1"
        assert d["time"] == "2024-03-01T12:00:00"
        assert d["data"] == {"key": "value"}

    def test_to_json(self):
        evt = func.CloudEvent(
            id="ce2", source="s", type="t", specversion="1.0", data=None
        )
        parsed = json.loads(evt.to_json())
        assert parsed["id"] == "ce2"


class TestSerializableNonBreaking(unittest.TestCase):
    """Verify that subclassing a binding ABC without implementing to_dict()
    does not break instantiation - the error is deferred to call time."""

    def _make_custom_queue_message(self):
        """Return a minimal concrete subclass of _abc.QueueMessage that
        implements only the pre-existing abstract surface, not to_dict()."""
        import azure.functions._abc as azf_abc

        class CustomQueueMessage(azf_abc.QueueMessage):
            @property
            def id(self):
                return "x"

            def get_body(self):
                return b"body"

            def get_json(self):
                return "body"

            @property
            def dequeue_count(self):
                return None

            @property
            def expiration_time(self):
                return None

            @property
            def insertion_time(self):
                return None

            @property
            def time_next_visible(self):
                return None

            @property
            def pop_receipt(self):
                return None

        return CustomQueueMessage

    def test_subclass_without_to_dict_can_be_instantiated(self):
        # Must not raise TypeError at instantiation time.
        cls = self._make_custom_queue_message()
        msg = cls()
        assert msg.id == "x"

    def test_subclass_without_to_dict_raises_at_call_time(self):
        cls = self._make_custom_queue_message()
        msg = cls()
        with self.assertRaises(NotImplementedError):
            msg.to_dict()

    def test_subclass_without_to_dict_to_json_raises_at_call_time(self):
        cls = self._make_custom_queue_message()
        msg = cls()
        with self.assertRaises(NotImplementedError):
            msg.to_json()
