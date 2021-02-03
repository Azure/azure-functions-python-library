# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import os
from typing import Callable, List, Dict, NamedTuple
from logging import Logger
from ._abc import Context


class FuncExtensionHookMeta(NamedTuple):
    ext_name: str
    impl: Callable


# Defines kinds of hook that we support
class FuncExtensionHooks(NamedTuple):
    before_invocation: List[FuncExtensionHookMeta] = []
    after_invocation: List[FuncExtensionHookMeta] = []


class FuncExtension(abc.ABC):
    """An abstract class defines the lifecycle hooks which to be implemented
    by customer's extension. Everytime when a new extension is initialized in
    customer's trigger, the _instances field will record it and will be
    executed by Python worker.
    """
    _instances: Dict[str, FuncExtensionHooks] = {}

    @abc.abstractmethod
    def __init__(self, trigger_name: str):
        """Constructor for extension. This needs to be implemented and ensure
        super().__init__(trigger_name) is called.

        The initializer serializes the extension to a tree. This speeds
        up the worker lookup and reduce the overhead on each invocation.
        _instances[<trigger_name>].<hook_name>.(ext_name, impl)

        Parameters
        ----------
        trigger_name: str
            The name of trigger the extension attaches to (e.g. HttpTrigger).
        """
        ext_hooks = FuncExtension._instances.setdefault(
            trigger_name.lower(),
            FuncExtensionHooks()
        )

        for hook_name in ext_hooks._fields:
            hook_impl = getattr(self, hook_name, None)
            if hook_impl is not None:
                getattr(ext_hooks, hook_name).append(FuncExtensionHookMeta(
                    ext_name=self.__class__.__name__,
                    impl=hook_impl
                ))

    # DO NOT decorate this with @abc.abstratmethod
    # since implementation is not mandatory
    def before_invocation(self, logger: Logger, context: Context,
                          *args, **kwargs) -> None:
        """A lifecycle hook to be implemented by the extension. This method
        will be called right before customer's function.

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
    # since implementation is not mandatory
    def after_invocation(self, logger: Logger, context: Context,
                         *args, **kwargs) -> None:
        """A lifecycle hook to be implemented by the extension. This method
        will be called right after customer's function.

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
    def get_hooks_of_trigger(cls, trigger_name: str) -> FuncExtensionHooks:
        """Return all function extension hooks indexed by trigger name.

        Parameters
        ----------
        trigger_name: str
            The trigger name
        """
        return cls._instances.get(trigger_name.lower(), FuncExtensionHooks())

    @classmethod
    def register_to_trigger(cls, filename: str) -> 'FuncExtension':
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
