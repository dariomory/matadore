"""Matadore input handlers.

Each handler resolves a target string into concrete assets for the scanning
plugins.  The engine selects the correct handler by matching the ``type=``
argument of ``engage()`` against :attr:`BaseInput.target_type`.

Available handlers::

    from matadore.inputs import (
        DomainInput,
        NetworkInput,
        RepoInput,
        GitHubOrgInput,
        CloudInput,
        DockerRegistryInput,
    )

The :data:`REGISTRY` mapping is used by the engine to look up handlers at
runtime without manual branching::

    handler = REGISTRY[target.type]()
    assets = handler.resolve(target)
"""

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset
from matadore.inputs.cloud import CloudInput
from matadore.inputs.docker_registry import DockerRegistryInput
from matadore.inputs.domain import DomainInput
from matadore.inputs.github_org import GitHubOrgInput
from matadore.inputs.network import NetworkInput
from matadore.inputs.repo import RepoInput

REGISTRY: dict[str, type[BaseInput]] = {
    "domain": DomainInput,
    "network": NetworkInput,
    "repo": RepoInput,
    "github_org": GitHubOrgInput,
    "cloud": CloudInput,
    "docker_registry": DockerRegistryInput,
}

__all__ = [
    "REGISTRY",
    "BaseInput",
    "CloudInput",
    "DockerRegistryInput",
    "DomainInput",
    "EngageTarget",
    "GitHubOrgInput",
    "NetworkInput",
    "RepoInput",
    "ResolvedAsset",
]
