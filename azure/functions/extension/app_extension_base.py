# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
import typing
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
    def init(cls):
        """The function will be executed when the extension is loaded.
        Happens when Azure Functions customers import the extension module.
        """
        pass

    @abc.abstractclassmethod
    def configure(cls, *args, **kwargs):
        """This function is intended to be called by Azure Functions
        customers. This is a contract between extension developers and
        azure functions customers. If multiple .configure() are called,
        the extension system cannot guarentee the calling order.
        """
        pass

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def after_function_load_global(cls,
                                   function_name: str,
                                   function_directory: str,
                                   *args, **kwargs) -> None:
        """This must be implemented as a @classmethod. It will be called right
        a customer's function is loaded. In this stage, the customer's logger
        is not fully initialized. Please use print() statement if necessary.

        Parameters
        ----------
        function_name: str
            The name of customer's function (e.g. HttpTrigger)
        function_directory: str
            The path to customer's function directory
            (e.g. /home/site/wwwroot/HttpTrigger)
        """
        pass

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def before_invocation_global(cls,
                                 context: Context,
                                 func_args: typing.Dict[str, object] = {},
                                 *args,
                                 **kwargs) -> None:
        """This must be implemented as a @staticmethod. It will be called right
        before a customer's function is being executed. In this stage, the
        ustomer's logger is not fully initialized, so it is not provided.

        Parameters
        ----------
        logger: logging.Logger
            A logger provided by Python worker. Extension developer should
            use this logger to emit telemetry to Azure Functions customers.
        context: azure.functions.Context
            This will include the function_name, function_directory and an
            invocation_id of this specific invocation.
        func_args: typing.Dict[str, object]
            Arguments that are passed into the Azure Functions. The name of
            each parameter is defined in function.json. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific trigger types or input binding types.
        """
        pass

    # DO NOT decorate this with @abc.abstractstatismethod
    # since implementation by subclass is not mandatory
    @classmethod
    def after_invocation_global(cls,
                                logger: Logger,
                                context: Context,
                                func_args: typing.Dict[str, object] = {},
                                func_ret: typing.Optional[object] = None,
                                *args,
                                **kwargs) -> None:
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
        func_args: typing.Dict[str, object]
            Arguments that are passed into the Azure Functions. The name of
            each parameter is defined in function.json. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific trigger types or input binding types.
        func_ret: typing.Optional[object]
            Return value from Azure Functions. This is usually the value
            defined in function.json $return section. Extension developers
            may also want to do isinstance() check if you want to apply
            operations to specific types or input binding types."
        """
        pass
