# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import importlib


def _agent_provider_distribution(provider: str) -> str:
    normalized = provider.replace('_', '-')
    if normalized.startswith('agent-'):
        normalized = normalized.removeprefix('agent-')
    return f'azurefunctions-extensions-agents-{normalized}'


def _load_agents_base(provider: str):
    try:
        return importlib.import_module('azurefunctions.extensions.agents.base')
    except ModuleNotFoundError as exc:
        missing_base_modules = {
            'azurefunctions',
            'azurefunctions.extensions',
            'azurefunctions.extensions.agents',
            'azurefunctions.extensions.agents.base',
        }
        if exc.name not in missing_base_modules:
            raise
        distribution = _agent_provider_distribution(provider)
        raise ImportError(
            f"Agent provider {provider!r} is not installed. "
            f"Install {distribution!r}."
        ) from exc
