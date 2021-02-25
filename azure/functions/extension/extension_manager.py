# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import abc
from typing import Dict
from .app_extension_hooks import AppExtensionHooks
from .app_extension_base import AppExtensionBase
from .func_extension_hooks import FuncExtensionHooks
from .func_extension_base import FuncExtensionBase
from .extension_hook_meta import ExtensionHookMeta
from .extension_scope import ExtensionScope


class ExtensionManager(abc.ABCMeta):
    _func_exts: Dict[str, FuncExtensionHooks] = {}
    _app_exts: AppExtensionHooks = AppExtensionHooks()

    @classmethod
    def get_extension_scope(self, class) -> ExtensionScope:
        if isinstance(class, AppExtensionBase):


    @classmethod
    def set_hooks_for_trigger(cls, trigger_name: str, ext):
        ext_hooks = cls._func_exts.setdefault(
            trigger_name.lower(),
            FuncExtensionHooks()
        )

        for hook_name in ext_hooks._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                getattr(ext_hooks, hook_name).append(ExtensionHookMeta(
                    ext_name=ext.__class__.__name__,
                    ext_impl=hook_impl
                ))

    @classmethod
    def set_hooks_for_app(cls, ext):
        for hook_name in cls._app_exts._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                getattr(cls._app_exts, hook_name).append(ExtensionHookMeta(
                    ext_name=ext.__class__.__name__,
                    ext_impl=hook_impl
                ))

    @classmethod
    def get_hooks_from_trigger(cls, trigger_name: str) -> FuncExtensionHooks:
        """Return all function extension hooks indexed by trigger name."""
        return cls._func_exts.get(trigger_name.lower(), FuncExtensionHooks())

    @classmethod
    def get_hooks_from_app(cls) -> AppExtensionHooks:
        """Return all application hooks"""
        return cls._app_exts
