# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from enum import Enum


class ExtensionScope(Enum):
    """There are two valid scopes of the worker extension framework.

    APPLICATION:
        It is injected in AppExtensionBase._scope. Any implementation of
        AppExtensionBase will be applied into all triggers.

    FUNCTION:
        It is injected in FuncExtensionBase._scope. Any implementation of
        FuncExtensionBase requires initialization in customer's function app
        trigger.
    """
    UNKNOWN = 0
    APPLICATION = 1
    FUNCTION = 2
