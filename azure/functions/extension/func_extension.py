# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import NamedTuple, List
import abc
import os
from logging import Logger
from .extension_hook_meta import ExtensionHookMeta
from .extension_meta import ExtensionMeta
from .._abc import Context


# Defines the life-cycle hooks we support in a single trigger
class FuncExtensionHooks(NamedTuple):
    after_function_load: List[ExtensionHookMeta] = []
    before_invocation: List[ExtensionHookMeta] = []
    after_invocation: List[ExtensionHookMeta] = []


class FuncExtension(metaclass=ExtensionMeta):
    """An abstract class defines the life-cycle hooks which to be implemented
    by customer's extension.

    Everytime when a new extension is initialized in customer function scripts,
    the ExtensionManager._func_exts field records the extension to this
    specific function name.
    """

    @abc.abstractmethod
    def __init__(self, trigger_name: str):
        """Constructor for extension. This needs to be implemented and ensure
        super().__init__(trigger_name) is called.

        The initializer serializes the extension to a tree. This speeds
        up the worker lookup and reduce the overhead on each invocation.
        _func_exts[<trigger_name>].<hook_name>.(ext_name, ext_impl)

        Parameters
        ----------
        trigger_name: str
            The name of trigger the extension attaches to (e.g. HttpTrigger).
        """
        ExtensionMeta.set_hooks_for_trigger(trigger_name, self)

    # DO NOT decorate this with @abc.abstratmethod
    # since implementation by subclass is not mandatory
    def after_function_load(self, logger: Logger,
                            function_name: str,
                            function_directory: str,
                            *args, **kwargs) -> None:
        """This hook will be called right after a customer's function is loaded

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
        pass


    # DO NOT decorate this with @abc.abstratmethod
    # since implementation by subclass is not mandatory
    def before_invocation(self, logger: Logger, context: Context,
                          *args, **kwargs) -> None:
        """This hook will be called right before customer's function
        is being executed.

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

    # DO NOT decorate this with @abc.abstratmethod
    # since implementation by subclass is not mandatory
    def after_invocation(self, logger: Logger, context: Context,
                         *args, **kwargs) -> None:
        """This hook will be called right after a customer's function
        is executed.

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

    @classmethod
    def register_to_function(cls, filename: str) -> 'FuncExtension':
        """Register extension to a specific trigger. Derive trigger name from
        script filepath and AzureWebJobsScriptRoot environment variable.

        Parameters
        ----------
        filename: str
            The path to current trigger script. Usually, pass in __file__.

        Returns
        -------
        FuncExtension
            The extension or its subclass
        """
        script_root = os.getenv('AzureWebJobsScriptRoot')
        if script_root is None:
            raise ValueError(
                'AzureWebJobsScriptRoot environment variable is not defined. '
                'Please ensure the extension is running in Azure Functions.'
            )

        try:
            trigger_name = os.path.split(
                os.path.relpath(
                    os.path.abspath(filename),
                    os.path.abspath(script_root)
                )
            )[0]
        except IndexError:
            raise ValueError(
                'Failed to parse trigger name from filename. Please ensure '
                '__file__ is passed into the filename argument'
            )

        return cls(trigger_name)