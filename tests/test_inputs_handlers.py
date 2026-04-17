"""Unit tests for all six input handler stubs."""

import pytest

from matadore.inputs import REGISTRY, CloudInput, DockerRegistryInput, DomainInput, GitHubOrgInput, NetworkInput, RepoInput
from matadore.inputs.base import EngageTarget


class TestDomainInput:
    def test_target_type(self):
        assert DomainInput.target_type == "domain"

    def test_dry_run_returns_asset(self):
        h = DomainInput()
        t = EngageTarget(value="example.com", dry_run=True)
        assets = h.resolve(t)
        assert len(assets) == 1
        assert assets[0].asset == "example.com"
        assert assets[0].asset_type == "domain"

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            DomainInput().resolve(EngageTarget(value="example.com"))

    def test_describe_contains_target(self):
        desc = DomainInput().describe(EngageTarget(value="example.com"))
        assert "example.com" in desc
        assert "DOMAIN" in desc

    def test_describe_passive_mode(self):
        desc = DomainInput().describe(EngageTarget(value="x.com", mode="passive"))
        assert "passive" in desc.lower() or "CT" in desc


class TestNetworkInput:
    def test_target_type(self):
        assert NetworkInput.target_type == "network"

    def test_dry_run_counts_hosts(self):
        h = NetworkInput()
        t = EngageTarget(value="192.168.1.0/24", type="network", dry_run=True)
        assets = h.resolve(t)
        assert assets[0].metadata["host_count"] == 254

    def test_dry_run_invalid_cidr_does_not_raise(self):
        h = NetworkInput()
        t = EngageTarget(value="not-a-cidr", type="network", dry_run=True)
        assets = h.resolve(t)
        assert assets[0].asset == "not-a-cidr"

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            NetworkInput().resolve(EngageTarget(value="10.0.0.0/8", type="network"))

    def test_describe_shows_host_count(self):
        desc = NetworkInput().describe(EngageTarget(value="10.0.0.0/24", type="network"))
        assert "254" in desc
        assert "NETWORK" in desc


class TestRepoInput:
    def test_target_type(self):
        assert RepoInput.target_type == "repo"

    def test_dry_run_returns_asset(self):
        assets = RepoInput().resolve(EngageTarget(value="myorg/myrepo", type="repo", dry_run=True))
        assert assets[0].asset == "myorg/myrepo"
        assert assets[0].asset_type == "repo"

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            RepoInput().resolve(EngageTarget(value="myorg/myrepo", type="repo"))

    def test_describe(self):
        desc = RepoInput().describe(EngageTarget(value="myorg/myrepo", type="repo"))
        assert "REPO" in desc
        assert "myorg/myrepo" in desc


class TestGitHubOrgInput:
    def test_target_type(self):
        assert GitHubOrgInput.target_type == "github_org"

    def test_dry_run_returns_asset(self):
        assets = GitHubOrgInput().resolve(
            EngageTarget(value="myorg", type="github_org", dry_run=True)
        )
        assert assets[0].asset == "myorg"
        assert assets[0].asset_type == "github_org"

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            GitHubOrgInput().resolve(EngageTarget(value="myorg", type="github_org"))

    def test_describe(self):
        desc = GitHubOrgInput().describe(EngageTarget(value="myorg", type="github_org"))
        assert "GITHUB_ORG" in desc
        assert "myorg" in desc


class TestCloudInput:
    def test_target_type(self):
        assert CloudInput.target_type == "cloud"

    def test_dry_run_aws_default(self):
        t = EngageTarget(value="my-account", type="cloud", dry_run=True)
        assets = CloudInput().resolve(t)
        assert assets[0].metadata["provider"] == "aws"

    def test_dry_run_gcp_provider(self):
        t = EngageTarget(value="my-project", type="cloud", dry_run=True, extra={"provider": "gcp"})
        assets = CloudInput().resolve(t)
        assert assets[0].metadata["provider"] == "gcp"

    def test_invalid_provider_raises(self):
        t = EngageTarget(value="x", type="cloud", extra={"provider": "heroku"})
        with pytest.raises(ValueError, match="Unsupported cloud provider"):
            CloudInput().resolve(t)

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            CloudInput().resolve(EngageTarget(value="x", type="cloud"))

    def test_describe_includes_provider(self):
        t = EngageTarget(value="x", type="cloud", extra={"provider": "gcp"})
        desc = CloudInput().describe(t)
        assert "GCP" in desc
        assert "CLOUD" in desc


class TestDockerRegistryInput:
    def test_target_type(self):
        assert DockerRegistryInput.target_type == "docker_registry"

    def test_dry_run_returns_asset(self):
        t = EngageTarget(value="myorg/myimage", type="docker_registry", dry_run=True)
        assets = DockerRegistryInput().resolve(t)
        assert assets[0].asset == "myorg/myimage"
        assert assets[0].asset_type == "docker_image"

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            DockerRegistryInput().resolve(
                EngageTarget(value="myorg/myimage", type="docker_registry")
            )

    def test_describe(self):
        t = EngageTarget(value="myorg/myimage", type="docker_registry")
        desc = DockerRegistryInput().describe(t)
        assert "DOCKER" in desc
        assert "myorg/myimage" in desc


class TestRegistry:
    def test_all_types_present(self):
        for typ in ("domain", "network", "repo", "github_org", "cloud", "docker_registry"):
            assert typ in REGISTRY

    def test_registry_returns_correct_classes(self):
        assert REGISTRY["domain"] is DomainInput
        assert REGISTRY["network"] is NetworkInput
        assert REGISTRY["repo"] is RepoInput
        assert REGISTRY["github_org"] is GitHubOrgInput
        assert REGISTRY["cloud"] is CloudInput
        assert REGISTRY["docker_registry"] is DockerRegistryInput

    def test_registry_instances_are_base_input_subclasses(self):
        from matadore.inputs.base import BaseInput
        for cls in REGISTRY.values():
            assert issubclass(cls, BaseInput)
