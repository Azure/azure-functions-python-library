# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import importlib

_AGENTS_BASE_MODULE = 'azurefunctions.extensions.agents.base'


def _agent_provider_distribution(provider: str) -> str:
    normalized = provider.replace('_', '-')
    if normalized.startswith('agent-'):
        normalized = normalized.removeprefix('agent-')
    return f'azurefunctions-extensions-agents-{normalized}'


def _load_agents_base(provider: str):
    try:
        return importlib.import_module(_AGENTS_BASE_MODULE)
    except ModuleNotFoundError as exc:
        distribution = _agent_provider_distribution(provider)
        raise ImportError(
            f"Agent provider {provider!r} is not installed. "
            f"Install {distribution!r}."
        ) from exc
