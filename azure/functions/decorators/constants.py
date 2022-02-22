#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import inspect
from abc import ABCMeta
from enum import Enum


class StringifyEnum(Enum):
    """This class output name of enum object when printed as string."""

    def __str__(self):
        return str(self.name)


class BuildDictMeta(type):
    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        setattr(cls, '__init__',
                cls.add_to_dict(getattr(cls, '__init__')))
        setattr(cls, 'get_dict_repr',
                cls.skip_none(getattr(cls, 'get_dict_repr')))
        return cls

    @staticmethod
    def skip_none(func):
        def wrapper(*args, **kw):
            res = func(*args, **kw)
            return BuildDictMeta.clean_nones(res)

        return wrapper

    @staticmethod
    def add_to_dict(func):
        def wrapper(*args, **kw):
            func(*args, **kw)
            setattr(args[0], 'init_params',
                    list(inspect.signature(func).parameters.keys()))

        return wrapper

    @staticmethod
    def clean_nones(value):
        """
        Recursively remove all None values from dictionaries and lists,
        and returns
        the result as a new dictionary or list.
        """
        if isinstance(value, list):
            return [BuildDictMeta.clean_nones(x) for x in value if
                    x is not None]
        elif isinstance(value, dict):
            return {
                key: BuildDictMeta.clean_nones(val)
                for key, val in value.items()
                if val is not None
            }
        else:
            return value


class ABCBuildDictMeta(ABCMeta, BuildDictMeta):
    pass


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
