# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
from typing import Dict
from .extension_manager import ExtensionManager


class ExtensionMeta(abc.ABCMeta):

    def __new__(cls, class_name, parents, attributes):
        new_ext = super().__new__(cls, class_name, parents, attributes)
        print(f'Extension Registered __new__: class_name:{class_name}')
        print(f'Extension Registered __new__: parents:{parents}')
        print(f'Extension Registered __new__:  attributes:{attributes}')
        return new_ext

    def __call__(self, *args, **kwargs):
        print(f'THIS IS BEING CALLED {args}')