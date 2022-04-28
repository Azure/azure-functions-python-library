# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from ._abc import TimerRequest, InputStream, Context, Out
from ._eventhub import EventHubEvent
from ._eventgrid import EventGridEvent, EventGridOutputEvent
from ._cosmosdb import Document, DocumentList
from ._http import HttpRequest, HttpResponse
from .decorators import (FunctionApp, Function, BluePrint,
                         DecoratorApi, DataType, AuthLevel,
                         Cardinality, AccessRights, HttpMethod,
                         AsgiFunctionApp, WsgiFunctionApp)
from ._durable_functions import OrchestrationContext, EntityContext
from .decorators.function_app import FunctionRegister, TriggerApi, \
    BindingApi, \
    ThirdPartyHttpFunctionApp
from .extension import (ExtensionMeta, FunctionExtensionException,
                        FuncExtensionBase, AppExtensionBase)
from ._http_wsgi import WsgiMiddleware
from ._http_asgi import AsgiMiddleware
from .kafka import KafkaEvent, KafkaConverter, KafkaTriggerConverter
from .meta import get_binding_registry
from ._queue import QueueMessage
from ._servicebus import ServiceBusMessage

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
    'EventGridOutputEvent',
    'EventHubEvent',
    'HttpRequest',
    'HttpResponse',
    'InputStream',
    'KafkaEvent',
    'KafkaConverter',
    'KafkaTriggerConverter',
    'OrchestrationContext',
    'EntityContext',
    'QueueMessage',
    'ServiceBusMessage',
    'TimerRequest',

    # Middlewares
    'WsgiMiddleware',
    'AsgiMiddleware',

    # Extensions
    'AppExtensionBase',
    'FuncExtensionBase',
    'ExtensionMeta',
    'FunctionExtensionException',

    # PyStein implementation
    'FunctionApp',
    'Function',
    'FunctionRegister',
    'DecoratorApi',
    'TriggerApi',
    'BindingApi',
    'BluePrint',
    'ThirdPartyHttpFunctionApp',
    'AsgiFunctionApp',
    'WsgiFunctionApp',
    'DataType',
    'AuthLevel',
    'Cardinality',
    'AccessRights',
    'HttpMethod'
)

__version__ = '1.11.0'
