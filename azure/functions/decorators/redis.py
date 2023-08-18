#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from typing import Optional

from azure.functions.decorators.constants import REDIS_PUBSUB_TRIGGER, REDIS_LIST_TRIGGER, REDIS_STREAM_TRIGGER
from azure.functions.decorators.core import Trigger, DataType

class RedisPubSubTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return REDIS_PUBSUB_TRIGGER

    def __init__(self,
                 name: str,
                 connectionStringSetting: str,
                 channel: str,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        self.connectionStringSetting = connectionStringSetting
        self.channel = channel
        super().__init__(name=name, data_type=data_type)

class RedisListTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return REDIS_LIST_TRIGGER

    def __init__(self,
                 name: str,
                 connectionStringSetting: str,
                 key: str,
                 pollingIntervalInMs: Optional[int] = 1000,
                 messagesPerWorker: Optional[int] = 100,
                 count: Optional[int] = 10,
                 listPopFromBeginning: Optional[bool] = True,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        self.connectionStringSetting = connectionStringSetting
        self.key = key
        self.pollingIntervalInMs = pollingIntervalInMs
        self.messagesPerWorker = messagesPerWorker
        self.count = count
        self.listPopFromBeginning = listPopFromBeginning
        super().__init__(name=name, data_type=data_type)

class RedisStreamTrigger(Trigger):
    @staticmethod
    def get_binding_name() -> str:
        return REDIS_STREAM_TRIGGER

    def __init__(self,
                 name: str,
                 connectionStringSetting: str,
                 key: str,
                 pollingIntervalInMs: Optional[int] = 1000,
                 messagesPerWorker: Optional[int] = 100,
                 count: Optional[int] = 10,
                 deleteAfterProcess: Optional[bool] = True,
                 data_type: Optional[DataType] = None,
                 **kwargs) -> None:
        self.connectionStringSetting = connectionStringSetting
        self.key = key
        self.pollingIntervalInMs = pollingIntervalInMs
        self.messagesPerWorker = messagesPerWorker
        self.count = count
        self.deleteAfterProcess = deleteAfterProcess
        super().__init__(name=name, data_type=data_type)
