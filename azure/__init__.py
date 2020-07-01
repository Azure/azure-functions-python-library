# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from pkgutil import extend_path
import typing

__path__: typing.Iterable[str] = extend_path(__path__, __name__)
