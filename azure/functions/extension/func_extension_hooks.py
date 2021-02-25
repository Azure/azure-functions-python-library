# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import NamedTuple, List
from .extension_hook_meta import ExtensionHookMeta


# Defines the life-cycle hooks we support in a single trigger
class FuncExtensionHooks(NamedTuple):
    after_function_load: List[ExtensionHookMeta] = []
    before_invocation: List[ExtensionHookMeta] = []
    after_invocation: List[ExtensionHookMeta] = []