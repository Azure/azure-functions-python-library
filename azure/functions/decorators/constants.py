#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
from enum import Enum


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


# binding types
COSMOS_DB = "cosmosDB"
COSMOS_DB_TRIGGER = "cosmosDBTrigger"
EVENT_HUB_TRIGGER = "eventHubTrigger"
EVENT_HUB = "eventHub"
HTTP_TRIGGER = "httpTrigger"
HTTP = "http"
QUEUE = "queue"
QUEUE_TRIGGER = "queueTrigger"
SERVICE_BUS = "serviceBus"
SERVICE_BUS_TRIGGER = "serviceBusTrigger"
TIMER_TRIGGER = "timerTrigger"
