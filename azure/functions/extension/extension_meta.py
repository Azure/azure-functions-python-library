# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Optional, Dict
import abc
import os
from .app_extension_hooks import AppExtensionHooks
from .func_extension_hooks import FuncExtensionHooks
from .extension_hook_meta import ExtensionHookMeta
from .extension_scope import ExtensionScope
from .extension_exception import ExtensionException


class ExtensionMeta(abc.ABCMeta):
    _func_exts: Dict[str, FuncExtensionHooks] = {}
    _app_exts: Optional[AppExtensionHooks] = None

    def __init__(cls, *args, **kwargs):
        scope = ExtensionMeta._get_extension_scope(cls)
        instance = super(ExtensionMeta, cls).__init__(*args, **kwargs)

        if scope is ExtensionScope.APPLICATION:
            ExtensionMeta._register_application_extension(instance)

        return instance

    def __call__(cls, *args, **kwargs):
        scope = ExtensionMeta._get_extension_scope(cls)

        if scope is ExtensionScope.FUNCTION:
            instance = super(ExtensionMeta, cls).__call__(*args, **kwargs)
            ExtensionMeta._register_function_extension(instance)
            return instance
        elif scope is ExtensionScope.APPLICATION:
            raise ExtensionException(
                f'Python worker extension:{cls.__name__} with scope:{scope} '
                'is not instantiateble. Please use class properties directly.')
        else:
            raise ExtensionException(
                f'Python worker extension:{cls.__name__} is not properly '
                'implemented from AppExtensionBase or FuncExtensionBase.'
            )

    @classmethod
    def set_hooks_for_function(cls, trigger_name: str, ext):
        ext_hooks = cls._func_exts.setdefault(
            trigger_name.lower(),
            cls._create_default_function_hook()
        )

        for hook_name in ext_hooks._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                getattr(ext_hooks, hook_name).append(ExtensionHookMeta(
                    ext_name=ext.__class__.__name__,
                    ext_impl=hook_impl
                ))

    @classmethod
    def set_hooks_for_application(cls, ext):
        if cls._app_exts is None:
            cls._app_exts = cls._create_default_app_hook()

        # Check for definition in AppExtensionHooks NamedTuple (e.g. )
        for hook_name in cls._app_exts._fields:
            hook_impl = getattr(ext, hook_name, None)
            if hook_impl is not None:
                getattr(cls._app_exts, hook_name).append(ExtensionHookMeta(
                    ext_name=ext.__class__.__name__,
                    ext_impl=hook_impl
                ))

    @classmethod
    def get_function_hooks(cls, name: str) -> Optional[FuncExtensionHooks]:
        """Return all function extension hooks indexed by trigger name."""
        return cls._func_exts.get(name.lower())

    @classmethod
    def get_applicaiton_hooks(cls) -> Optional[AppExtensionHooks]:
        """Return all application hooks"""
        return cls._app_exts

    @classmethod
    def _get_extension_scope(cls, extension) -> ExtensionScope:
        return getattr(extension, '_scope', ExtensionScope.UNKNOWN)

    @classmethod
    def _register_function_extension(cls, extension) -> str:
        trigger_name = extension._trigger_name
        cls.set_hooks_for_function(trigger_name, extension)

    @classmethod
    def _register_application_extension(cls, extension) -> str:
        cls.set_hooks_for_app(extension)

    @classmethod
    def _create_default_function_hook(cls) -> FuncExtensionHooks:
        return FuncExtensionHooks(
            after_function_load=[],
            before_invocation=[],
            after_invocation=[]
        )

    @classmethod
    def _create_default_app_hook(cls) -> AppExtensionHooks:
        return AppExtensionHooks(
            after_function_load_global=[],
            before_invocation_global=[],
            after_invocation_global=[]
        )