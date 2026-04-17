"""Unit tests for the five built-in plugin stubs."""

import pytest

from matadore.plugins import GitLeaks, Nmap, Nuclei, ScoutSuite, Trivy
from matadore.plugins.base import PluginContext


class TestNmap:
    def test_name(self):
        assert Nmap.name == "nmap"

    def test_supported_types(self):
        p = Nmap()
        assert p.supports("domain") is True
        assert p.supports("network") is True
        assert p.supports("cloud") is False

    def test_dry_run_returns_skipped(self):
        p = Nmap()
        ctx = PluginContext(dry_run=True)
        result = p.run("example.com", ctx)
        assert result.skipped is True
        assert "example.com" in result.skip_reason

    def test_active_raises_not_implemented(self):
        p = Nmap()
        ctx = PluginContext(dry_run=False)
        with pytest.raises(NotImplementedError):
            p.run("example.com", ctx)


class TestNuclei:
    def test_name(self):
        assert Nuclei.name == "nuclei"

    def test_supported_types(self):
        p = Nuclei()
        assert p.supports("domain") is True
        assert p.supports("network") is True
        assert p.supports("repo") is False

    def test_dry_run_returns_skipped(self):
        p = Nuclei()
        result = p.run("example.com", PluginContext(dry_run=True))
        assert result.skipped is True

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            Nuclei().run("example.com", PluginContext())


class TestTrivy:
    def test_name(self):
        assert Trivy.name == "trivy"

    def test_supported_types(self):
        p = Trivy()
        assert p.supports("docker_registry") is True
        assert p.supports("repo") is True
        assert p.supports("domain") is False

    def test_dry_run_returns_skipped(self):
        result = Trivy().run("myorg/myimage", PluginContext(dry_run=True))
        assert result.skipped is True
        assert "myorg/myimage" in result.skip_reason

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            Trivy().run("myorg/myimage", PluginContext())


class TestGitLeaks:
    def test_name(self):
        assert GitLeaks.name == "gitleaks"

    def test_supported_types(self):
        p = GitLeaks()
        assert p.supports("repo") is True
        assert p.supports("github_org") is True
        assert p.supports("network") is False

    def test_dry_run_returns_skipped(self):
        result = GitLeaks().run("myorg/myrepo", PluginContext(dry_run=True))
        assert result.skipped is True
        assert "myorg/myrepo" in result.skip_reason

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            GitLeaks().run("myorg/myrepo", PluginContext())


class TestScoutSuite:
    def test_name(self):
        assert ScoutSuite.name == "scoutsuite"

    def test_supported_types(self):
        p = ScoutSuite()
        assert p.supports("cloud") is True
        assert p.supports("domain") is False

    def test_dry_run_returns_skipped(self):
        result = ScoutSuite().run("my-aws-account", PluginContext(dry_run=True))
        assert result.skipped is True
        assert "my-aws-account" in result.skip_reason

    def test_active_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ScoutSuite().run("my-aws-account", PluginContext())


class TestPluginsPackageImports:
    def test_all_builtins_importable(self):
        from matadore.plugins import BasePlugin, GitLeaks, Nmap, Nuclei, PluginContext, PluginResult, ScoutSuite, Trivy

        for cls in (BasePlugin, Nmap, Nuclei, Trivy, GitLeaks, ScoutSuite, PluginContext, PluginResult):
            assert cls is not None
