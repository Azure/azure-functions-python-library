# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from ._abc import TimerRequest, InputStream, Context, Out  # NoQA
from ._eventhub import EventHubEvent  # NoQA
from ._eventgrid import EventGridEvent, EventGridOutputEvent  # NoQA
from ._cosmosdb import Document, DocumentList  # NoQA
from ._http import HttpRequest  # NoQA
from ._http import HttpResponse  # NoQA
from ._http_wsgi import WsgiMiddleware # NoQA
from .kafka import KafkaEvent, KafkaConverter, KafkaTriggerConverter  # NoQA
from ._queue import QueueMessage  # NoQA
from ._servicebus import ServiceBusMessage  # NoQA
from ._durable_functions import OrchestrationContext  # NoQA
from .meta import get_binding_registry  # NoQA

# Import binding implementations to register them
from . import blob  # NoQA
from . import cosmosdb  # NoQA
from . import eventgrid  # NoQA
from . import eventhub  # NoQA
from . import http  # NoQA
from . import kafka # NoQA
from . import queue  # NoQA
from . import servicebus  # NoQA
from . import timer  # NoQA
from . import durable_functions  # NoQA


__all__ = (
    # Functions
    'get_binding_registry',

    # Generics.
    'Context',
    'Out',

    # Binding rich types, sorted alphabetically.
    'Document',
    'DocumentList',
    'EventGridEvent',
    'EventHubEvent',
    'HttpRequest',
    'HttpResponse',
    'InputStream',
    'KafkaEvent',
    'KafkaConverter',
    'KafkaTriggerConverter',
    'OrchestrationContext',
    'QueueMessage',
    'ServiceBusMessage',
    'TimerRequest',

    # Middlewares
    'WsgiMiddleware'
)

__version__ = '1.3.1'
