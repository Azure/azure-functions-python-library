#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import unittest

from azure.functions.decorators.constants import REDIS_PUBSUB_TRIGGER, REDIS_LIST_TRIGGER, REDIS_STREAM_TRIGGER
from azure.functions.decorators.core import BindingDirection, DataType
from azure.functions.decorators.redis import RedisPubSubTrigger, RedisListTrigger, RedisStreamTrigger


class TestRedis(unittest.TestCase):
    def test_pubsub_trigger_valid_creation(self):
        trigger = RedisPubSubTrigger(name="req",
                               connectionStringSetting="dummy_connection",
                               channel="dummy_channel",
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "redisPubSubTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": REDIS_PUBSUB_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "connectionStringSetting": "dummy_connection",
            "channel": "dummy_channel"
        })

    def test_list_trigger_valid_creation(self):
        trigger = RedisListTrigger(name="req",
                               connectionStringSetting="dummy_connection",
                               key="dummy_key",
                               pollingIntervalInMs=1,
                               messagesPerWorker=2,
                               count=3,
                               listPopFromBeginning=False,
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "redisListTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": REDIS_LIST_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "connectionStringSetting": "dummy_connection",
            "channel": "dummy_channel",
            "pollingIntervalInMs": 1,
            "messagesPerWorker": 2,
            "count": 3,
            "listPopFromBeginning": False,
        })

    def test_stream_trigger_valid_creation(self):
        trigger = RedisStreamTrigger(name="req",
                               connectionStringSetting="dummy_connection",
                               key="dummy_key",
                               pollingIntervalInMs=1,
                               messagesPerWorker=2,
                               count=3,
                               deleteAfterProcess=True,
                               data_type=DataType.UNDEFINED,
                               dummy_field="dummy")

        self.assertEqual(trigger.get_binding_name(), "redisStreamTrigger")
        self.assertEqual(trigger.get_dict_repr(), {
            "type": REDIS_STREAM_TRIGGER,
            "direction": BindingDirection.IN,
            'dummyField': 'dummy',
            "name": "req",
            "dataType": DataType.UNDEFINED,
            "connectionStringSetting": "dummy_connection",
            "channel": "dummy_channel",
            "pollingIntervalInMs": 1,
            "messagesPerWorker": 2,
            "count": 3,
            "deleteAfterProcess": True,
        })
