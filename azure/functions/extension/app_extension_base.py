# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
from logging import Logger
from .extension_meta import ExtensionMeta
from .extension_scope import ExtensionScope
from .._abc import Context


class AppExtensionBase(metaclass=ExtensionMeta):
    """An abstract class defines the global life-cycle hooks to be implemented
    by customer's extension, will be applied to all functions.

    An AppExtension should be treated as a static class. Must not contain
    __init__ method since it is not instantiable.

    Please place your initialization code in setup() function.
    """

    _scope = ExtensionScope.APPLICATION

    @abc.abstractclassmethod
    def setup(cls):
        """The setup function to be implemented when the extension is loaded
        """
        pass

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def after_function_load_global(cls,
                                   logger: Logger,
                                   function_name: str,
                                   function_directory: str,
                                   *args, **kwargs) -> None:
        """This must be implemented as a @classmethod. It will be called right
        a customer's function is loaded

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        function_name: str
            The name of customer's function (e.g. HttpTrigger)
        function_directory: str
            The path to customer's function directory
            (e.g. /home/site/wwwroot/HttpTrigger)
        """

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def before_invocation_global(cls, logger: Logger, context: Context,
                                 *args, **kwargs) -> None:
        """This must be implemented as a @staticmethod. It will be called right
        before a customer's function is being executed.

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        context: azure.functions.Context
            This will include the function_name, function_directory and an
            invocation_id of this specific invocation.
        """
        pass

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def after_invocation_global(cls, logger: Logger, context: Context,
                                *args, **kwargs) -> None:
        """This must be implemented as a @staticmethod. It will be called right
        before a customer's function is being executed.

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        context: azure.functions.Context
            This will include the function_name, function_directory and an
            invocation_id of this specific invocation.
        """
        pass
