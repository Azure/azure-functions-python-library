# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import NamedTuple, List
from .extension_hook_meta import ExtensionHookMeta


# Defines the life-cycle hooks we support for all triggers in a function app
class AppExtensionHooks(NamedTuple):
    # The default values are not being set here intentionally since it is
    # impacted by a Python bug https://bugs.python.org/issue33077.
    after_function_load_global: List[ExtensionHookMeta]
    before_invocation_global: List[ExtensionHookMeta]
    after_invocation_global: List[ExtensionHookMeta]