# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import importlib

_AGENTS_BASE_MODULE = 'azurefunctions.extensions.agents.base'
_agents_base = None


def _agent_provider_distribution(provider: str) -> str:
    normalized = provider.replace('_', '-')
    return f'azurefunctions-agents-extension-{normalized}'


def _import_agents_base():
    global _agents_base
    if _agents_base is None:
        _agents_base = importlib.import_module(_AGENTS_BASE_MODULE)
    return _agents_base


def _load_agents_base(provider: str):
    try:
        return _import_agents_base()
    except ImportError as exc:
        distribution = _agent_provider_distribution(provider)
        raise ImportError(
            f"Agent provider {provider!r} is not installed. "
            f"Install {distribution!r}."
        ) from exc
