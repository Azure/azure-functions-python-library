# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Callable, NamedTuple


class ExtensionHookMeta(NamedTuple):
    ext_name: str
    ext_impl: Callable